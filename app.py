from altair.vegalite.v4.api import value
import lasio
from numpy.core.fromnumeric import mean
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from fpdf import FPDF
import base64
from tempfile import NamedTemporaryFile
# from pyxlsb import open_workbook as open_xlsb
# from io import BytesIO

sns.set(style='ticks')

st.set_option('deprecation.showfileUploaderEncoding', False)

st.title('Welcome to Petrophysics Plotter!')
st.text('Plot your LAS 2.0 file into a triple combo and/or formation evaluation plots.\n(c) 2021, Aditya Arie Wijaya\n=============================')
st.text('Suggestions --> LinkedIn: www.linkedin.com/in/adityaariewijaya89')
st.text('Documentation: https://github.com/ariewjy/triple_combo_web_plotter')
st.text('Running Process may take longer, be patient and reload when stucked')

st.title('LAS File Data')

mode = st.radio(
    "Select an option:",
    ('Upload File', 'Use Preloaded File')
)

if mode == 'Upload File':
    file = st.file_uploader('Upload the LAS file')
    
if mode == 'Use Preloaded File':
    file = '42303347740000.las'


if file:
  las_file = lasio.read(file)
  las_df=las_file.df()    
  las_df.insert(0, 'DEPTH', las_df.index)
  las_df.reset_index(drop=True, inplace=True) 

  

  well_name =  las_file.header['Well'].WELL.value
  start_depth =  las_file.header['Well'].STRT.value
  stop_depth =  las_file.header['Well'].STOP.value
  company_name =  las_file.header['Well'].COMP.value
  date =  las_file.header['Well'].DATE.value
  curvename = las_file.curves
  

  st.subheader('Well Information')
  st.text(f'================================================\nWell Name : {well_name}')
  st.text(f'Start Depth : {start_depth}')
  st.text(f'Stop Depth : {stop_depth}')
  st.text(f'Company : {company_name}')
  st.text(f'Logging Date : {date}')
  
  st.subheader('Curve Information')
  st.text(f'================================================\n{curvename}')

  st.subheader('Curve Data')
  st.markdown('LAS file curve data is displayed as a table below, similar to excel sheet.\nMove left-right and up-down, or expand to see more')
  st.write(las_df)

  
 
#   for item in las_file.well:
#     st.text(f"{item.descr} ({item.mnemonic}): {item.value}")

  st.title('Selecting Curves')
  curves = las_df.columns.values
  
  if 'GR' in curves:
    gr_col = las_df.columns.get_loc('GR')
  else:
    gr_col = 0
  
  if 'ILD' in curves:
    res_col = las_df.columns.get_loc('ILD')
  else:
    res_col = 0

  if 'RHOB' in curves:
    den_col = las_df.columns.get_loc('RHOB')
  else:
    den_col = 0

  if 'NPHI' in curves:
    neu_col = las_df.columns.get_loc('NPHI')
  else:
    neu_col = 0
    
  gr_curve = st.selectbox('select the gamma ray curve', curves, index=gr_col)
  res_curve = st.selectbox('select the resistivity curve', curves, index=res_col)
  den_curve = st.selectbox('select the density curve', curves, index=den_col)
  neu_curve = st.selectbox('select the neutron curve', curves, index=neu_col)
  
  curve_list = [gr_curve, res_curve, den_curve, neu_curve]
  
#==========================
  
  st.sidebar.title('Plot Setting')
  well_name = st.sidebar.text_input('Well Name',value =(well_name))
  well_df = las_df
  curve_names = curve_list
  top_depth = st.sidebar.number_input('Top Depth', min_value=0.00, value=(start_depth), step=100.00)
  bot_depth = st.sidebar.number_input('Bottom Depth', min_value=0.00, value=(stop_depth), step=100.00)

  plot_w = 12
  plot_h = 17

  title_size = 12
  title_height = 1.0
  line_width = 1

  st.sidebar.title('Gamma Ray Logs')
  gr_color = 'green'
  gr_trackname = f'Gamma Ray ({gr_curve})'
  gr_left = st.sidebar.slider('Gamma Ray Left Scale', min_value=0, value=0, step=10)
  gr_right = st.sidebar.slider('Gamma Ray Right Scale', min_value=0, value=200, max_value=300, step=10)
  gr_cutoff = st.sidebar.slider('Gamma Ray Cutoff', min_value=0, value=60)
  gr_base = st.sidebar.slider('Gamma Ray Base', min_value=0, value=0)
  gr_shale = st.sidebar.radio('Shale Colour',['lime','gray','none'])
  gr_sand = st.sidebar.radio('Sand Colour',['gold','yellow', 'none'])
  if gr_right == 150:
    gr_div = 6
  else:
    gr_div=5

  st.sidebar.title('Resistivity Logs')
  res_color = 'purple'
  res_trackname = f'Resistivity ({res_curve})'
  res_left = st.sidebar.number_input('Resistivity Left Scale', min_value=0.0001, max_value=1000000.0000, value=0.2)
  res_right = st.sidebar.number_input('Resistivity Right Scale', min_value=0.0001, max_value=1000000.0000, value = 20000.0000)
  res_cutoff = st.sidebar.number_input('Resistivity Cutoff', min_value=0.01, max_value=1000.00, value=100.00)
  res_shading = st.sidebar.radio('Resistivity Shading',['none','lightcoral', 'lightgreen'])

  st.sidebar.title('Density Logs')
  den_color = 'red'
  den_trackname = f'Density ({den_curve})'
  den_left = st.sidebar.number_input('Density Left Scale', min_value=0.00, value=1.95, step=0.05)
  den_right = st.sidebar.number_input('Density Right Scale', max_value=3.00, value=2.95, step=0.05)

  st.sidebar.title('Neutron Logs')
  neu_color = 'blue'
  neu_trackname = f'Neutron ({neu_curve})'
  neu_mean = np.nanmean(las_df[str(neu_curve)])
  if neu_mean < 1 :
    neu_left = st.sidebar.number_input('Neutron Left Scale', min_value=-50.00, value=0.45)
    neu_right = st.sidebar.number_input('Neutron Right Scale', min_value=-50.00, value=-0.15)
  if neu_mean > 1:
    neu_left = st.sidebar.number_input('Neutron Left Scale', min_value=-50.00, value=45.00)
    neu_right = st.sidebar.number_input('Neutron Right Scale', min_value=-50.00, value=-15.00)

  den_neu_div = st.sidebar.radio('Number of Division:',[5,6])
  dn_xover = st.sidebar.radio('D-N Colour',['yellow','gold','none'])
  dn_sep = st.sidebar.radio('N-D Colour',['lightgray','green', 'none'])


#=================
  st.title('Triple Combo Plot')
#   st.write('Right Click and Save as Image to Download the File')

  fig, ax = plt.subplots(figsize=(plot_w,plot_h))
  fig.suptitle(f"Triple Combo Plot\n===================\nWell: {well_name}\n(Interval: {top_depth} - {bot_depth})\n===================\n ---(c) Aditya Arie Wijaya,2021---\nhttps://github.com/ariewjy\n===================",
              size=title_size, y=title_height)

  gr_log=las_df[curve_list[0]]
  res_log=las_df[curve_list[1]]
  den_log=las_df[curve_list[2]]
  neu_log=las_df[curve_list[3]]

  #Set up the plot axes
  ax1 = plt.subplot2grid((1,3), (0,0), rowspan=1, colspan = 1)
  ax2 = plt.subplot2grid((1,3), (0,1), rowspan=1, colspan = 1)
  ax3 = plt.subplot2grid((1,3), (0,2), rowspan=1, colspan = 1)
  ax4 = ax3.twiny() #Twins the y-axis for the density track with the neutron track

  #adding top border
  ax7 = ax1.twiny()
  ax7.xaxis.set_visible(False)
  ax8 = ax2.twiny()
  ax8.xaxis.set_visible(False)
  ax9 = ax3.twiny()
  ax9.xaxis.set_visible(False)

  # Gamma Ray track
  ax1.plot(gr_log, "DEPTH", data = well_df, color = gr_color, lw=line_width)
  ax1.set_xlabel(gr_trackname)
  ax1.set_xlim(gr_left, gr_right)
  ax1.set_ylim(bot_depth, top_depth)
  ax1.xaxis.label.set_color(gr_color)
  ax1.tick_params(axis='x', colors=gr_color)
  ax1.spines["top"].set_edgecolor(gr_color)
  ax1.spines["top"].set_position(("axes", 1.02))
  ax1.set_xticks(list(np.linspace(gr_left, gr_right, num = gr_div)))

  ax1.grid(which='major', color='lightgrey', linestyle='-')
  ax1.xaxis.set_ticks_position("top")
  ax1.xaxis.set_label_position("top")

  ##area-fill sand and shale from gr
  ax1.fill_betweenx(well_df['DEPTH'], gr_base, gr_log, where=(gr_cutoff >= gr_log), interpolate=True, color = gr_sand, linewidth=0)
  ax1.fill_betweenx(well_df['DEPTH'], gr_base, gr_log, where=(gr_cutoff <= gr_log), interpolate=True, color = gr_shale, linewidth=0)

  # RES track
  ax2.plot(res_log, "DEPTH", data = well_df, color = res_color, lw=line_width)
  ax2.set_xlabel(res_trackname)
  ax2.set_xlim(res_left, res_right)
  ax2.set_ylim(bot_depth, top_depth)
  ax2.semilogx()
  ax2.minorticks_on()
  ax2.xaxis.grid(which='minor', linestyle=':', linewidth='0.5', color='gray')   
  ax2.xaxis.label.set_color(res_color)
  ax2.tick_params(axis='x', colors=res_color)
  ax2.spines["top"].set_edgecolor(res_color)
  ax2.spines["top"].set_position(("axes", 1.02))

  ax2.grid(which='major', color='lightgrey', linestyle='-')
  ax2.xaxis.set_ticks_position("top")
  ax2.xaxis.set_label_position("top")


  ax2.fill_betweenx(well_df['DEPTH'], res_cutoff, res_log, where=(res_log >= res_cutoff), interpolate=True, color = res_shading, linewidth=0)

  # Density track
  ax3.plot(den_log, "DEPTH", data = well_df, color = den_color, lw=line_width)
  ax3.set_xlabel(den_trackname)
  ax3.set_xlim(den_left, den_right)
  ax3.set_ylim(bot_depth, top_depth)
  ax3.xaxis.label.set_color(den_color)
  ax3.tick_params(axis='x', colors=den_color)
  ax3.spines["top"].set_edgecolor(den_color)
  ax3.spines["top"].set_position(("axes", 1.02))
  ax3.set_xticks(list(np.linspace(den_left, den_right, num = den_neu_div)))

  ax3.grid(which='major', color='lightgrey', linestyle='-')
  ax3.xaxis.set_ticks_position("top")
  ax3.xaxis.set_label_position("top")

  # Neutron trak placed ontop of density track
  ax4.plot(neu_log, "DEPTH", data = well_df, color = neu_color, lw=line_width)
  ax4.set_xlabel(neu_trackname)
  ax4.xaxis.label.set_color(neu_color)
  ax4.set_xlim(neu_left, neu_right)
  ax4.set_ylim(bot_depth, top_depth)
  ax4.tick_params(axis='x', colors=neu_color)
  ax4.spines["top"].set_position(("axes", 1.08))
  ax4.spines["top"].set_visible(True)
  ax4.spines["top"].set_edgecolor(neu_color)
  ax4.set_xticks(list(np.linspace(neu_left, neu_right, num = den_neu_div)))

  #shading between density and neutron
  x1=den_log
  x2=neu_log

  x = np.array(ax3.get_xlim())
  z = np.array(ax4.get_xlim())

  nz=((x2-np.max(z))/(np.min(z)-np.max(z)))*(np.max(x)-np.min(x))+np.min(x)

  ax3.fill_betweenx(well_df['DEPTH'], x1, nz, where=x1>=nz, interpolate=True, color=dn_sep, linewidth=0)
  ax3.fill_betweenx(well_df['DEPTH'], x1, nz, where=x1<=nz, interpolate=True, color=dn_xover, linewidth=0)


  #end
      

  plt.tight_layout()

  # if savepdf is True:
  # pdf.add_image(temp_file.name)
  # file = plt.savefig((f"{well_name}_triple_combo_plot.pdf"), dpi=150, bbox_inches='tight')
  # st.download_button(label='Download Plot as PDF',data= file)

  plt.show() 
  st.pyplot(fig)
  
  #download feature
  def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

  export_as_pdf = st.button("Export Triple Combo Plot to PDF")

  if export_as_pdf:
    pdf = FPDF()
    pdf.add_page()
    with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
      fig.savefig(tmpfile.name)
      pdf.image(tmpfile.name, 10, 10, (plot_w*16), (plot_h*16))
    html = create_download_link(pdf.output(dest="S").encode("latin-1"), f'{well_name} - Triple Combo')
    st.markdown(html, unsafe_allow_html=True)

st.title(' ')


####### VSH-------------...
mode = st.radio(
    "Activate Formation Evaluation Module?",
    ('Not Now', 'Yes Please!')
)

if mode == 'Yes Please!':

  st.title('Formation Evaluation')

  #sidebar-vsh
  st.sidebar.title('Volume of Shale')
  mode = st.sidebar.radio(
      "Calculate VSH from:",
      ('Gamma-Ray', 'Density-Neutron')
  )

  if mode == 'Gamma-Ray':
    gr_min = st.sidebar.number_input('GR at 0% Shale', min_value=0, value=10, step=10)
    gr_max = st.sidebar.number_input('GR at 100% Shale', min_value=0, value=150, max_value=300, step=10)
    # st.write(gr_log)
    vsh_log = (gr_log - gr_min)/(gr_max-gr_min) * 100
    vsh_log = np.clip(vsh_log, 0, 100)
    vsh_color = 'black'
    well_df['VSH'] = vsh_log

  if neu_mean > 1 :
    neu_log = neu_log/100
  else:
    neu_log=neu_log
  if mode == 'Density-Neutron':
    denmat = st.sidebar.number_input('Matrix-Density', min_value=1.0, value=2.65, step=0.1)
    denfl = st.sidebar.number_input('Fluid-Density', min_value=0.0, value=1.0, max_value=1.5, step=0.1)
    dphi = (denmat - den_log)/(denmat-denfl)
    den_shale = st.sidebar.number_input('Density at 100% Shale', min_value=1.0, value=2.7, step=0.1)
    dphi_shale = (den_shale - den_log)/(den_shale-denfl)
    dphi_shale = np.clip(dphi_shale, 0, 1)
    neu_shale = st.sidebar.number_input('Neutron at 100% Shale', min_value=0.0, value=0.35, step=0.1)
    neu_mean = neu_log.mean()
    # st.write(neu_mean)
    

    vsh_log = (neu_log - dphi)/(neu_shale-dphi_shale) *100
    vsh_log = np.clip(vsh_log, 0, 100)
    vsh_color = 'black'
    well_df['VSH'] = vsh_log

    
  shale_shading = st.sidebar.radio('Shale Shading',['green','gray'])
  sand_shading = st.sidebar.radio('Sand/Carbonate Shading',['gold','royalblue'])

  vsh_trackname = f'Vshale {mode} (%)\n'

    #sidebar-porosity
  st.sidebar.title('Porosity')
  mode = st.sidebar.radio(
    "Choose the Porosity Method",
    ('Density-Neutron', 'Density')
  )
  if mode == 'Density':
    density_mat = st.sidebar.number_input('Matrix Density', min_value=1.0, value=2.65, step=0.1)
    density_fluid = st.sidebar.number_input('Fluid Density', min_value=0.0, value=1.0, max_value=1.5, step=0.1)
    dphi_log = (density_mat - den_log)/(density_mat-density_fluid)
    # dphi_left = st.sidebar.number_input('Left DPHI Scale', min_value=0.0, max_value=1.0, value=0.5, step=0.1)
    # dphi_right = st.sidebar.number_input('Right DPHI Scale', min_value=0.0, max_value=1.0, value=0.0, step=0.1)
    # dphi_color = 'black'
    tpor_log = dphi_log  
    tpor_log = np.clip(tpor_log, 0.001, 1)
    epor_log = tpor_log*(1-vsh_log/100)
    epor_log = np.clip(epor_log, 0.001, 1)

  if mode == 'Density-Neutron':
    density_mat = st.sidebar.number_input('Matrix Density', min_value=1.0, value=2.65, step=0.1)
    density_fluid = st.sidebar.number_input('Fluid Density', min_value=0.0, value=1.0, max_value=1.5, step=0.1)
    dphi_log = (density_mat - den_log)/(density_mat-density_fluid)
    dnphi_log = ((dphi_log**2 + neu_log**2)/2)**0.5
    # dphi_left = st.sidebar.number_input('Left DPHI Scale', min_value=0.0, max_value=1.0, value=0.5, step=0.1)
    # dphi_right = st.sidebar.number_input('Right DPHI Scale', min_value=0.0, max_value=1.0, value=0.0, step=0.1)
    # dphi_color = 'black'
    tpor_log = dnphi_log
    tpor_log = np.clip(tpor_log, 0.001, 1)
    epor_log = tpor_log*(1-vsh_log/100)
    epor_log = np.clip(epor_log, 0.001, 1)

  mode = st.sidebar.radio(
    "Porosity to Display",
    ('Effective Porosity', 'Total Porosity')
  )
  if mode == 'Total Porosity':
    por_log = tpor_log*100
  if mode == 'Effective Porosity':
    por_log = epor_log*100

  well_df['TPOR'] = tpor_log
  well_df['EPOR'] = epor_log

  por_left = st.sidebar.number_input('Left Scale', min_value=0, max_value=100, value=50, step=10)
  por_right = st.sidebar.number_input('Right Scale', min_value=0, max_value=100, value=0, step=10)
  por_color = 'black'
  por_shading = st.sidebar.radio('Total Porosity Shading',['aqua','none'])
  # sand_shading = st.sidebar.radio('Sand Shading',['gold','yellow'])

  por_trackname = f'Porosity (p.u.)\n'

  #sidebar-Sw
  st.sidebar.title('Water Saturation')
  mode = st.sidebar.radio(
    "Calculate Rw from Salinity and Temp",
    ('No, I have my own Rw', 'Yes, Please!')
  )
  if mode == 'Yes, Please!':
    water_sal = st.sidebar.number_input ('Input Salinity in NaCl ppm', min_value=0, value =25000)
    fm_temp = st.sidebar.number_input('Formation Temperature in Fahrenheit', min_value=10, value = 75)
    rw_calc = (400000 / fm_temp / water_sal) ** 0.88
    st.sidebar.subheader(f'The Calculated Rw = {round(rw_calc,3)} ohm-m')
  rw = st.sidebar.number_input('Formation Water Resistivity (Rw)', min_value=0.0, value=0.05, step=0.01)
  a_value = st.sidebar.number_input('Turtuosity Factor (a)', min_value=0.0, value=1.0, max_value=10.0, step=0.1)
  m_value = st.sidebar.number_input('Porosity Exponent (m)', min_value=0.0, value=2.0, max_value=10.0, step=0.1)
  n_value = st.sidebar.number_input('Saturation Exponent (n)', min_value=0.0, value=2.0, max_value=10.0, step=0.1)
  # atas = rw/res_log
  # bawah = por_log**m_value
  # sw_log = (atas/bawah)**(1/n_value)
  por_input = por_log/100
  sw_log = (rw/(res_log*por_input**m_value))**(a_value/n_value)*100
  sw_log = np.clip(sw_log, 0, 100)
  sw_color = 'black'
  hc_shading = st.sidebar.radio('Hydrocarbon Shading',['lime','coral'])
  well_df['SW'] = sw_log

  # shale_shading = st.sidebar.radio('Shale Shading',['green','gray'])
  # sand_shading = st.sidebar.radio('Sand Shading',['gold','yellow'])
  sw_left = 100
  sw_right = 0
  sw_trackname = f'Water Saturation (%)\n'

  fig, ax = plt.subplots(figsize=(plot_w,plot_h))
  fig.suptitle(f"Formation Evaluation Plot\n===================\nWell: {well_name}\n(Interval: {top_depth} - {bot_depth})\n===================\n ---(c) Aditya Arie W,2021---\nhttps://github.com/ariewjy\n===================",
              size=title_size, y=title_height)

  #Set up the plot axes
  ax1 = plt.subplot2grid((1,3), (0,0), rowspan=1, colspan = 1)
  ax2 = plt.subplot2grid((1,3), (0,1), rowspan=1, colspan = 1)
  ax3 = plt.subplot2grid((1,3), (0,2), rowspan=1, colspan = 1)
  # ax4 = ax3.twiny() #Twins the y-axis for the density track with the neutron track

  #adding top border
  ax7 = ax1.twiny()
  ax7.xaxis.set_visible(False)
  ax8 = ax2.twiny()
  ax8.xaxis.set_visible(False)
  ax9 = ax3.twiny()
  ax9.xaxis.set_visible(False)

  # Vsh track
  ax1.plot(vsh_log, "DEPTH", data = well_df, color = vsh_color, lw=line_width)
  ax1.set_xlabel(vsh_trackname)
  ax1.set_xlim(0, 100)
  ax1.set_ylim(bot_depth, top_depth)
  ax1.xaxis.label.set_color(vsh_color)
  ax1.tick_params(axis='x', colors=vsh_color)
  ax1.spines["top"].set_edgecolor(vsh_color)
  ax1.spines["top"].set_position(("axes", 1.02))
  ax1.set_xticks(list(np.linspace(0, 100, num = 5)))

  ax1.grid(which='major', color='lightgrey', linestyle='-')
  ax1.xaxis.set_ticks_position("top")
  ax1.xaxis.set_label_position("top")

  ##area-fill sand and shale for VSH
  ax1.fill_betweenx(well_df['DEPTH'], 0, vsh_log, interpolate=False, color = shale_shading, linewidth=0)
  ax1.fill_betweenx(well_df['DEPTH'], vsh_log, 100, interpolate=False, color = sand_shading, linewidth=0)


  # Porosity track
  ax2.plot(por_log, "DEPTH", data = well_df, color = por_color, lw=line_width)
  ax2.set_xlabel(por_trackname)
  ax2.set_xlim(por_left, por_right)
  ax2.set_ylim(bot_depth, top_depth)
  ax2.xaxis.label.set_color(por_color)
  ax2.tick_params(axis='x', colors=por_color)
  ax2.spines["top"].set_edgecolor(por_color)
  ax2.spines["top"].set_position(("axes", 1.02))
  ax2.set_xticks(list(np.linspace(por_left, por_right, num = 6)))

  ax2.grid(which='major', color='lightgrey', linestyle='-')
  ax2.xaxis.set_ticks_position("top")
  ax2.xaxis.set_label_position("top")

  ##area-fill tpor and epor
  ax2.fill_betweenx(well_df['DEPTH'], por_log, 0, interpolate=True, color = por_shading, linewidth=0)
  # ax2.fill_betweenx(well_df['DEPTH'], vsh_log, 100, interpolate=True, color = sand_shading, linewidth=0)


  # Sw track
  ax3.plot(sw_log, "DEPTH", data = well_df, color = sw_color, lw=line_width)
  ax3.set_xlabel(sw_trackname)
  ax3.set_xlim(sw_left, sw_right)
  ax3.set_ylim(bot_depth, top_depth)
  ax3.xaxis.label.set_color(sw_color)
  ax3.tick_params(axis='x', colors=sw_color)
  ax3.spines["top"].set_edgecolor(sw_color)
  ax3.spines["top"].set_position(("axes", 1.02))
  ax3.set_xticks(list(np.linspace(sw_left, sw_right, num = 6)))

  ax3.grid(which='major', color='lightgrey', linestyle='-')
  ax3.xaxis.set_ticks_position("top")
  ax3.xaxis.set_label_position("top")

  ##area-fill sw
  ax3.fill_betweenx(well_df['DEPTH'], 100, sw_log, interpolate=True, color = hc_shading, linewidth=0)
  ax3.fill_betweenx(well_df['DEPTH'], sw_log, 0, interpolate=True, color = 'lightblue', linewidth=0)

  plt.tight_layout()

  plt.show() 
  st.pyplot(fig)

  #download feature
  def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

  export_as_pdf = st.button("Export Formation Evaluation Plot to PDF")

  if export_as_pdf:
    pdf = FPDF()
    pdf.add_page()
    with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
      fig.savefig(tmpfile.name)
      pdf.image(tmpfile.name, 10, 10, (plot_w*16), (plot_h*16))
    html = create_download_link(pdf.output(dest="S").encode("latin-1"), f'{well_name} - Form Eval')
    st.markdown(html, unsafe_allow_html=True)

  # st.write(well_df)

  # Histogram

  st.title('Histogram')
  st.sidebar.title('Histogram')
  well_df = well_df.drop('DEPTH', axis=1, inplace=False)
  curve_hist = st.selectbox('select the curve for histogram', well_df.columns)
  scale_hist_left = st.sidebar.number_input ('Left Scale',value= well_df[curve_hist].min())
  scale_hist_right = st.sidebar.number_input ('Right Scale',value= well_df[curve_hist].max())
  agree = st.sidebar.checkbox('Logarithmic Scale')
  if agree:
    log_value_hist = True
  else:
    log_value_hist = False

  fig = px.histogram(well_df, x=curve_hist, log_x = log_value_hist, range_x=[scale_hist_left, scale_hist_right])

  st.plotly_chart(fig)
  
  # Scatter Plot
  st.title('Scatter Plot')
  st.sidebar.title('Scatter Plot')
  # well_df = well_df.drop('DEPTH', axis=1, inplace=False)
  x_curve = st.selectbox('select the curve for X-axis', well_df.columns)
  scale_x_left = st.sidebar.number_input ('Left Scale X-axis', value= well_df[x_curve].min())
  scale_x_right = st.sidebar.number_input ('Right Scale X-axis', value = well_df[x_curve].max())
  agreex = st.sidebar.checkbox('Logarithmic Scale on X')
  if agreex:
    log_valuex = True
  else:
    log_valuex=False
  y_curve = st.selectbox('select the curve for Y-axis', well_df.columns)
  scale_y_upper = st.sidebar.number_input ('Upper Scale Y-axis', value= well_df[y_curve].min())
  scale_y_bottom = st.sidebar.number_input ('Bottom Scale Y-axis', value = well_df[y_curve].max())
  agreey = st.sidebar.checkbox('Logarithmic Scale on Y')
  if agreey:
    log_valuey = True
  else:
    log_valuey=False
  z_curve = st.selectbox('select the curve for Z-axis', well_df.columns)
  scale_z_left = st.sidebar.number_input ('Bottom Scale Z-axis', value= well_df[z_curve].min())
  scale_z_right = st.sidebar.number_input ('Upper Scale Z-axis', value = well_df[z_curve].max())

  fig=px.scatter(well_df, x=x_curve, y=y_curve,log_y=log_valuey,log_x = log_valuex,
                color = z_curve, range_x=[scale_x_left, scale_x_right], range_y = [scale_y_bottom, scale_y_upper])

  st.plotly_chart(fig)

