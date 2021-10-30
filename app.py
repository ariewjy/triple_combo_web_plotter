import lasio
from numpy.core.fromnumeric import mean
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='ticks')


st.set_option('deprecation.showfileUploaderEncoding', False)

st.title('Welcome to Triple Combo Web-App Plotter')
st.text('This is a web app to plot your LAS 2.0 file data into a triple combo plot.\n(c) 2021, Aditya Arie Wijaya\n=============================')
st.text('LinkedIn: www.linkedin.com/in/adityaariewijaya89')
st.text('github: https://github.com/ariewjy')

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
  st.markdown('LAS file curve data is displayed as a table below, similar to excel sheet. Move left-right and up-down, or expand to see more.')
  st.write(las_df)

  
 
  # for item in las_file.well:
  #   st.text(f"{item.descr} ({item.mnemonic}): {item.value}")

  st.title('Selecting Curves')
  curves = las_df.columns.values

  # gr_col = las_df.columns.get_loc('GR')
  # res_col = las_df.columns.get_loc('ILD')
  # den_col = las_df.columns.get_loc('RHOB')
  # neu_col = las_df.columns.get_loc('NPHI')

  gr_curve = st.selectbox('select the gamma ray curve', curves)
  res_curve = st.selectbox('select the resistivity curve', curves)
  den_curve = st.selectbox('select the density curve', curves)
  neu_curve = st.selectbox('select the neutron curve', curves)

  curve_list = [gr_curve, res_curve, den_curve, neu_curve]

#==========================
  
  st.sidebar.title('Plot Setting')
  well_name = st.sidebar.text_input('Well Name',value =(well_name))
  well_df = las_df
  curve_names = curve_list
  top_depth = st.sidebar.number_input('Top Depth', min_value=0.00, value=(start_depth), step=100.00)
  bot_depth = st.sidebar.number_input('Bottom Depth', min_value=0.00, value=(stop_depth), step=100.00)

  plot_w = 12
  plot_h = 16

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
  res_left = st.sidebar.number_input('Resistivity Left Scale', min_value=0.0001, max_value=1000000.0000, value=0.02)
  res_right = st.sidebar.number_input('Resistivity Right Scale', min_value=0.0001, max_value=1000000.0000, value = 2000.0000)
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
  st.write('Right Click and Save as Image to Download the File')

  fig, ax = plt.subplots(figsize=(plot_w,plot_h))
  fig.suptitle(f"===================\nWell: {well_name}\n(Interval: {top_depth} - {bot_depth})\n===================\n ---(c) Aditya Arie Wijaya,2021---\nhttps://github.com/ariewjy\n===================",
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
    
  #   file = plt.savefig((f"{well_name}_triple_combo_plot.pdf"), dpi=150, bbox_inches='tight')
  #   st.download_button(label='Download Plot as PDF',data= file)

  plt.show() 
  st.pyplot(fig)



