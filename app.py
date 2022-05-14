
from cmath import nan
import lasio
import pathlib 
from numpy.core.fromnumeric import mean
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns    
import plotly.express as px
from fpdf import FPDF
from tempfile import NamedTemporaryFile
import tempfile
import streamlit.components.v1 as components
import striplog
from striplog import Legend, Lexicon, Interval, Component, Decor
import missingno as ms

litho='b'
limestone_strip = Decor({'component': Component({'hatch':litho}), 'hatch': litho, 'colour': '#eeeeee'}).plot(fmt="{hatch}")
# st.pyplot(limestone_strip)

sns.set(style='ticks')

st.set_option('deprecation.showfileUploaderEncoding', False)

st.title('Welcome to Petrophysics Plotter!')
st.text('Plot your LAS 2.0 file into a triple combo and/or formation evaluation plots.\n(c) 2021, Aditya Arie Wijaya\n=============================')
st.write('Find the source code in [**my Github repo**] (https://github.com/ariewjy/triple_combo_web_plotter) and reach me out in [**LinkedIn**] (www.linkedin.com/in/adityaariewijaya89)')
st.markdown('Support this web application by [donating as low as 1 USD] (https://ko-fi.com/plotpetrophysics)')

# st.write('Please reload when stucked. Enjoy!')
st.title('LAS File Data')

mode = st.radio(
    "Select an option:",
    ('Upload File', 'Use Preloaded File')
)

if mode == 'Upload File':
    file = st.file_uploader('Upload the LAS file')
    if file is not None:
      tfile = tempfile.NamedTemporaryFile(delete=False)
      tfile.write(file.read())
      las_file = lasio.read(tfile.name)
      las_df=las_file.df()
      

if mode == 'Use Preloaded File':
    file = '42303347740000.las'
    las_file = lasio.read(file)
    las_df=las_file.df()    


if file:  
  las_df.insert(0, 'DEPTH', las_df.index)
  las_df.reset_index(drop=True, inplace=True)   

  try:
    well_name =  las_file.header['Well'].WELL.value
    start_depth = las_df['DEPTH'].min()
    stop_depth = las_df['DEPTH'].max()
    step = abs(las_file.header['Well'].STEP.value)
    company_name =  las_file.header['Well'].COMP.value
    date =  las_file.header['Well'].DATE.value
    curvename = las_file.curves
  except:
    well_name =  'unknown'
    start_depth = 0.00
    stop_depth = 10000.00
    step = abs(las_df['DEPTH'][1]-las_df['DEPTH'][0])
    company_name =  'unknown'
    date =  'unknown'
    curvename = las_file.curves

  st.subheader('Well Information')
  st.text(f'================================================\nWell Name : {well_name}')
  st.text(f'Start Depth : {start_depth}')
  st.text(f'Stop Depth : {stop_depth}')
  st.text(f'Step : {step}')
  st.text(f'Company : {company_name}')
  st.text(f'Logging Date : {date}')
  
  st.subheader('Curve Information')
  st.text(f'================================================\n{curvename}')

  st.subheader('Curve Data Overview')
  st.markdown(f'The value on the left figure is number of rows. White space in each column of curve is a missing value rows/data. Expand to see more details')
  st.pyplot(ms.matrix(las_df, sparkline=False, labels=100).figure)

  # for item in las_file.well:
  #   st.text(f"{item.descr} ({item.mnemonic} {item.unit}): {item.value}")

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
    
  gr_curve = st.selectbox('select the GAMMA RAY curve', curves, index=gr_col)
  res_curve = st.selectbox('select the RESISTIVITY curve', curves, index=res_col)
  den_curve = st.selectbox('select the BULK DENSITY curve', curves, index=den_col)
  neu_curve = st.selectbox('select the NEUTRON POROSITY curve', curves, index=neu_col)
  
  curve_list = [gr_curve, res_curve, den_curve, neu_curve]
  
#==========================
  
  st.sidebar.title('Plot Setting')
  well_name = st.sidebar.text_input('Well Name',value =(well_name))
  well_df = las_df
  curve_names = curve_list
  top_depth = st.sidebar.number_input('Top Depth', min_value=0.00, value=(start_depth), step=100.00)
  bot_depth = st.sidebar.number_input('Bottom Depth', min_value=0.00, value=(stop_depth), step=100.00)

  plot_h = 17
  plot_w = 12

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
  gr_sand = st.sidebar.radio('Reservoir Colour',['gold','yellow', 'none'])
  gr_shale = st.sidebar.radio('Non-Reservoir Colour',['lime','gray','none'])

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

  den_neu_div = st.sidebar.radio('Number of Division:',[4,5])
  dn_xover = st.sidebar.radio('D-N Colour',['yellow','gold','none'])
  dn_sep = st.sidebar.radio('N-D Colour',['lightgray','green', 'none'])


#=================
  st.title('Triple Combo Plot')


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
  ax1.minorticks_on()
  ax1.set_xlim(gr_left, gr_right)
  ax1.set_ylim(bot_depth, top_depth)
  ax1.xaxis.label.set_color(gr_color)
  ax1.tick_params(axis='x', colors=gr_color)
  ax1.spines["top"].set_edgecolor(gr_color)
  ax1.spines["top"].set_position(("axes", 1.02))
  ax1.set_xticks(list(np.linspace(gr_left, gr_right, num = gr_div)))

  ax1.grid(which='major', color='silver', linestyle='-')
  ax1.grid(which='minor', color='lightgrey', linestyle=':', axis='y')
  ax1.xaxis.set_ticks_position("top")
  ax1.xaxis.set_label_position("top")

  ##area-fill sand and shale from gr
  ax1.fill_betweenx(well_df['DEPTH'], gr_base, gr_log, where=(gr_cutoff >= gr_log), interpolate=True, color = gr_sand, linewidth=0, alpha=0.8)
  ax1.fill_betweenx(well_df['DEPTH'], gr_base, gr_log, where=(gr_cutoff <= gr_log), interpolate=True, color = gr_shale, linewidth=0, alpha=0.8)

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

  ax2.grid(which='major', color='silver', linestyle='-')
  ax2.grid(which='minor', color='lightgrey', linestyle=':', axis='y')
  ax2.xaxis.set_ticks_position("top")
  ax2.xaxis.set_label_position("top")


  ax2.fill_betweenx(well_df['DEPTH'], res_cutoff, res_log, where=(res_log >= res_cutoff), interpolate=True, color = res_shading, linewidth=0)

  # Density track
  ax3.plot(den_log, "DEPTH", data = well_df, color = den_color, lw=line_width)
  ax3.set_xlabel(den_trackname)
  # ax3.minorticks_on()
  ax3.set_xlim(den_left, den_right)
  ax3.set_ylim(bot_depth, top_depth)
  ax3.xaxis.label.set_color(den_color)
  ax3.tick_params(axis='x', colors=den_color)
  ax3.spines["top"].set_edgecolor(den_color)
  ax3.spines["top"].set_position(("axes", 1.02))
  ax3.set_xticks(list(np.linspace(den_left, den_right, num = (den_neu_div+1))))

  ax3.grid(which='major', color='silver', linestyle='-')
  ax3.grid(which='minor', color='lightgrey', linestyle=':', axis='y')
  ax3.xaxis.set_ticks_position("top")
  ax3.xaxis.set_label_position("top")

  # Neutron trak placed ontop of density track
  ax4.plot(neu_log, "DEPTH", data = well_df, color = neu_color, lw=line_width)
  ax4.set_xlabel(neu_trackname)
  ax4.minorticks_on()
  ax4.xaxis.label.set_color(neu_color)
  ax4.set_xlim(neu_left, neu_right)
  ax4.set_ylim(bot_depth, top_depth)
  ax4.tick_params(axis='x', colors=neu_color)
  ax4.spines["top"].set_position(("axes", 1.08))
  ax4.spines["top"].set_visible(True)
  ax4.spines["top"].set_edgecolor(neu_color)
  ax4.set_xticks(list(np.linspace(neu_left, neu_right, num = (den_neu_div+1))))

  #shading between density and neutron
  x1=den_log
  x2=neu_log

  x = np.array(ax3.get_xlim())
  z = np.array(ax4.get_xlim())

  nz=((x2-np.max(z))/(np.min(z)-np.max(z)))*(np.max(x)-np.min(x))+np.min(x)

  ax3.fill_betweenx(well_df['DEPTH'], x1, nz, where=x1>=nz, interpolate=True, color=dn_sep, linewidth=0, alpha=0.8)
  ax3.fill_betweenx(well_df['DEPTH'], x1, nz, where=x1<=nz, interpolate=True, color=dn_xover, linewidth=0, alpha=0.8)

  plt.tight_layout()


  plt.show() 
  st.pyplot(fig)
  
  #download feature
  #exporting as pdf

  pdf = FPDF()
  pdf.add_page()
  with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
    fig.savefig(tmpfile.name)
    pdf.image(tmpfile.name, 10, 10, (plot_w*16), (plot_h*16))
  st.download_button(
    "Download Triple Combo Plot as PDF",
    data=pdf.output(dest='S').encode('latin-1'),
    file_name=f"{well_name}_triple_combo.pdf",
)

st.title(' ')


####### VSH-------------...
if file:
  formevalmode = st.checkbox("Formation Evaluation Module")

  if formevalmode:
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
      
      

      vsh_log = (neu_log - dphi)/(neu_shale-dphi_shale) *100
      vsh_log = np.clip(vsh_log, 0, 100)
      vsh_color = 'black'
      well_df['VSH'] = vsh_log

    shale_shading = st.sidebar.radio('Shale Shading',['green','gray'])
    sand_shading = st.sidebar.radio('Sand/Carbonate Shading',['Sandstone','Carbonate'])

    vsh_trackname = f'Vshale {mode} (%)\n'

    st.sidebar.title('Coal Flag')
    coal_flag = st.sidebar.checkbox('Coal Flag?')
    if coal_flag:
      neu_coal = st.sidebar.number_input('Neutron Coal', value = 0.25, step = 0.05)
      den_coal = st.sidebar.number_input('Density Coal', value = 2.00, step = 0.05)
    
      coal_index = np.where((neu_log>=neu_coal) & (den_log<=den_coal), 1, 0)
    else: 
      coal_index = np.nan

    well_df['COAL'] = coal_index
    

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
      
      tpor_log = dphi_log  
      tpor_log = np.clip(tpor_log, 0.001, 1)
      tpor_log = np.where((coal_index ==1), 0.001, tpor_log)
      epor_log = tpor_log*(1-vsh_log/100)
      epor_log = np.clip(epor_log, 0.001, 1)
      epor_log = np.where((coal_index ==1), 0.001, epor_log)

    if mode == 'Density-Neutron':
      density_mat = st.sidebar.number_input('Matrix Density', min_value=1.0, value=2.65, step=0.1)
      density_fluid = st.sidebar.number_input('Fluid Density', min_value=0.0, value=1.0, max_value=1.5, step=0.1)
      dphi_log = (density_mat - den_log)/(density_mat-density_fluid)
      dnphi_log = ((dphi_log**2 + neu_log**2)/2)**0.5
      
      tpor_log = dnphi_log
      tpor_log = np.clip(tpor_log, 0.001, 1)
      tpor_log = np.where((coal_index ==1), 0.001, tpor_log)
      epor_log = tpor_log*(1-vsh_log/100)
      epor_log = np.clip(epor_log, 0.001, 1)
      epor_log = np.where((coal_index ==1), 0.001, epor_log)
    
    
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

    por_left = st.sidebar.number_input('Left Scale', min_value=0, max_value=100, value=35, step=10)
    por_right = st.sidebar.number_input('Right Scale', min_value=0, max_value=100, value=0, step=10)
    por_grid = st.sidebar.number_input('Number of Grids', min_value = 0, value=8, step =1)
    por_color = 'black'
    por_shading = st.sidebar.radio('Total Porosity Shading',['aqua','none'])
    # sand_shading = st.sidebar.radio('Sand Shading',['gold','yellow'])

    por_trackname = f'Porosity (p.u.)\n'

    #sidebar-Sw
    st.sidebar.title('Water Saturation')
    rw_input = st.sidebar.checkbox("Input Rw")
    if rw_input:
      water_sal = st.sidebar.number_input ('Input Salinity in NaCl ppm', min_value=0, value =25000)
      fm_temp = st.sidebar.number_input('Formation Temperature in Fahrenheit', min_value=10, value = 75)
      rw_calc = (400000 / fm_temp / water_sal) ** 0.88
      st.sidebar.subheader(f'The Calculated Rw = {round(rw_calc,3)} ohm-m')
    rw = st.sidebar.number_input('Formation Water Resistivity (Rw)', min_value=0.0, value=0.05, step=0.01)
    a_value = st.sidebar.number_input('Turtuosity Factor (a)', min_value=0.0, value=1.0, max_value=10.0, step=0.1)
    m_value = st.sidebar.number_input('Porosity Exponent (m)', min_value=0.0, value=2.0, max_value=10.0, step=0.1)
    n_value = st.sidebar.number_input('Saturation Exponent (n)', min_value=0.0, value=2.0, max_value=10.0, step=0.1)
      
    por_input = por_log/100
    sw_log = (rw/(res_log*por_input**m_value))**(a_value/n_value)*100
    sw_log = np.clip(sw_log, 0, 100)
    sw_color = 'black'
    
    hc_shading = st.sidebar.radio('Hydrocarbon Shading',['lime','coral'])
    well_df['SW'] = sw_log

    st.sidebar.title('Pay Flag')
    pay_flag = st.sidebar.checkbox('Pay Flag')
    if pay_flag:
      # vsh_cutoff = st.sidebar.number_input('VSH Cutoff', value = 0.75, step = 0.05)
      epor_cutoff = st.sidebar.number_input('EPOR Cutoff', value = 0.1, step = 0.05)
      sw_cutoff = st.sidebar.number_input('SW Cutoff', value = 80, step = 5)
    
      pay_index = np.where((epor_log>epor_cutoff) & (sw_log<sw_cutoff), 1, 0)
    else: 
      pay_index = np.nan

    well_df['PAY'] = pay_index
      

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
    if coal_flag:
      ax4 = ax1.twiny() #Twins the y-axis for the density track with the neutron track
    if pay_flag:
      ax5 = ax3.twiny()
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
    ax1.minorticks_on()
    ax1.set_xlim(0, 100)
    ax1.set_ylim(bot_depth, top_depth)
    ax1.xaxis.label.set_color(vsh_color)
    ax1.tick_params(axis='x', colors=vsh_color)
    ax1.spines["top"].set_edgecolor(vsh_color)
    ax1.spines["top"].set_position(("axes", 1.02))
    ax1.set_xticks(list(np.linspace(0, 100, num = 5)))

    ax1.grid(which='major', color='grey', linestyle='--')
    ax1.grid(which='minor', color='lightgrey', linestyle='-.', axis='y')
    ax1.xaxis.set_ticks_position("top")
    ax1.xaxis.set_label_position("top")

    ##area-fill sand and shale for VSH
    ax1.fill_betweenx(well_df['DEPTH'], 0, vsh_log, interpolate=False, color = shale_shading, linewidth=0, alpha=0.5, hatch = '=-')
    if sand_shading is 'Carbonate':
      ax1.fill_betweenx(well_df['DEPTH'], vsh_log, 100, interpolate=False, color = 'cornflowerblue', linewidth=0, alpha=0.5, hatch = 'b')
    else:
      ax1.fill_betweenx(well_df['DEPTH'], vsh_log, 100, interpolate=False, color = 'gold', linewidth=0, alpha=0.5, hatch = 'o')
    


    # Porosity track
    ax2.plot(por_log, "DEPTH", data = well_df, color = por_color, lw=line_width)
    ax2.set_xlabel(por_trackname)
    ax2.minorticks_on()
    ax2.set_xlim(por_left, por_right)
    ax2.set_ylim(bot_depth, top_depth)
    ax2.xaxis.label.set_color(por_color)
    ax2.tick_params(axis='x', colors=por_color)
    ax2.spines["top"].set_edgecolor(por_color)
    ax2.spines["top"].set_position(("axes", 1.02))
    ax2.set_xticks(list(np.linspace(por_left, por_right, num = int(por_grid))))

    ax2.grid(which='major', color='grey', linestyle='--')
    ax2.grid(which='minor', color='lightgrey', linestyle='-.', axis='y')
    ax2.xaxis.set_ticks_position("top")
    ax2.xaxis.set_label_position("top")

    ##area-fill tpor and epor
    ax2.fill_betweenx(well_df['DEPTH'], por_log, 0, interpolate=True, color = por_shading, linewidth=0, alpha=0.5)
    # ax2.fill_betweenx(well_df['DEPTH'], vsh_log, 100, interpolate=True, color = sand_shading, linewidth=0)
    
    #coal track
    if coal_flag:
      ax4.plot(coal_index, "DEPTH", data = well_df, color = 'black', lw=2)
      ax4.set_xlabel('COAL')
      ax4.minorticks_on()
      ax4.xaxis.label.set_color('black')
      ax4.set_xlim(1, 0)
      ax4.set_ylim(bot_depth, top_depth)
      ax4.tick_params(axis='x', colors='black')
      ax4.spines["top"].set_position(("axes", 1.08))
      ax4.spines["top"].set_visible(True)
      ax4.spines["top"].set_edgecolor('black')
      ax4.set_xticks(list(np.linspace(1, 0, num = 2)))
      ax4.fill_betweenx(well_df['DEPTH'], coal_index, 0, interpolate=True, color = 'black', linewidth=0.0, alpha = 0.7)


    # Sw track
    ax3.plot(sw_log, "DEPTH", data = well_df, color = sw_color, lw=line_width)
    ax3.set_xlabel(sw_trackname)
    ax3.minorticks_on()
    ax3.set_xlim(sw_left, sw_right)
    ax3.set_ylim(bot_depth, top_depth)
    ax3.xaxis.label.set_color(sw_color)
    ax3.tick_params(axis='x', colors=sw_color)
    ax3.spines["top"].set_edgecolor(sw_color)
    ax3.spines["top"].set_position(("axes", 1.02))
    ax3.set_xticks(list(np.linspace(sw_left, sw_right, num = 6)))

    ax3.grid(which='major', color='grey', linestyle='--')
    ax3.grid(which='minor', color='lightgrey', linestyle='-.', axis='y')
    ax3.xaxis.set_ticks_position("top")
    ax3.xaxis.set_label_position("top")

    ##area-fill sw
    ax3.fill_betweenx(well_df['DEPTH'], 100, sw_log, interpolate=True, color = hc_shading, linewidth=0, alpha=0.5)
    ax3.fill_betweenx(well_df['DEPTH'], sw_log, 0, interpolate=True, color = 'lightblue', linewidth=0, alpha=0.5)

    if pay_flag:
      ax5.plot(pay_index, "DEPTH", data = well_df, color = 'red', lw=2)
      ax5.set_xlabel('PAY FLAG')
      ax5.minorticks_on()
      ax5.xaxis.label.set_color('red')
      ax5.set_xlim(10, 0)
      ax5.set_ylim(bot_depth, top_depth)
      ax5.tick_params(axis='x', colors='black')
      ax5.spines["top"].set_position(("axes", 1.08))
      ax5.spines["top"].set_visible(True)
      ax5.spines["top"].set_edgecolor('black')
      ax5.set_xticks(list(np.linspace(10, 0, num = 2)))
      ax5.fill_betweenx(well_df['DEPTH'], pay_index, 0, interpolate=True, color = 'red', linewidth=0.0, alpha = 0.7)

    plt.tight_layout()

    plt.show() 
    st.pyplot(fig)

    #exporting as pdf
    pdf = FPDF()
    pdf.add_page()
    with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
      fig.savefig(tmpfile.name)
      pdf.image(tmpfile.name, 10, 10, (plot_w*16), (plot_h*16))
    st.download_button(
      "Download Formation Evaluation Plot as PDF",
      data=pdf.output(dest='S').encode('latin-1'),
      file_name=f"{well_name}_formation_eval.pdf",
  )

    well_df= well_df.query(f"`DEPTH` >= {top_depth} and `DEPTH` <= {bot_depth}")
    st.markdown('**Final Result, Expand to See Full Data.**')
    st.text('VSH, TPOR, EPOR, and SW are in the Last Right 4 Columns')
    st.write (well_df)


    st.title('Downloading Final Result as CSV')
    st.markdown('**REMARKS**: _The CSV file will include input LAS data_ **AND** _Formation Evaluation Result: Volume of Shale (%), Porosity (dec), and Water Saturation (%) at the above depth interval_')

    #exporting as CSV
    @st.cache
    def convert_df(df):
      return df.to_csv().encode('utf-8')


    csv = convert_df(well_df)

    st.download_button(
      "Download the Formation Evaluation CSV file",
      csv,
      f"{well_name}_formation_eval.csv",
      "text/csv",
      key='download-csv'
    )

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
    

  #   @st.cache
    pdf = FPDF()
    pdf.add_page()
    with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
      fig.write_image(tmpfile.name)
      pdf.image(tmpfile.name, 10, 10, (plot_w*16), (plot_h*8))
    st.download_button(
      "Download Histogram as PDF",
      data=pdf.output(dest='S').encode('latin-1'),
      file_name=f"{well_name}_histogram_{curve_hist}.pdf",
  )

    # Scatter Plot
    st.title('Scatter Plot')
    st.sidebar.title('Scatter Plot')
  
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
    scale_z_left = st.sidebar.number_input ('Bottom Scale Z-axis', value= 0)
    scale_z_right = st.sidebar.number_input ('Upper Scale Z-axis', value = 100)

    fig=px.scatter(well_df, x=x_curve, y=y_curve,log_y=log_valuey,log_x = log_valuex,
                  color = z_curve, range_x=[scale_x_left, scale_x_right], range_y = [scale_y_bottom, scale_y_upper],
                  color_continuous_scale=px.colors.sequential.Aggrnyl_r)

    st.plotly_chart(fig)
    
  #   @st.cache
    pdf = FPDF()
    pdf.add_page()
    with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
      fig.write_image(tmpfile.name)
      pdf.image(tmpfile.name, 10, 10, (plot_w*16), (plot_h*8))
    st.download_button(
      "Download Scatter Plot as PDF",
      data=pdf.output(dest='S').encode('latin-1'),
      file_name=f"{well_name}_Crossplot_{x_curve}_{y_curve}_{z_curve}.pdf",
  )

