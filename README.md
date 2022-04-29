# Welcome to Online Petrophysics Plotter :wave:

## This is a documentation of online website to plot LAS file data into a triple combo plot and formation evaluation plot.

The website is available at __www.plotpetrophysics.xyz__ or __https://plotpetrophysics.xyz/__ (for SSL certificated website)

## Features:
- Adjustable depth, color, and curve-shading.
- Shading for shales, carbonate, and sandstone are using geological symbol
- A built in example from pre-loaded LAS file.
- Ability to calculate Rw from Salinity and Temperature.
- Ability to calculate VSH from Gamma-Ray or Density-Neutron logs.
- Ability to calculate porosity (total or effective) from Density only or Density-Neutron combination (Crossplot).
- Coal Flag with Neutron and Density Cutoffs. 
- Ability to calculate water saturation (Sw) using Archie's equation. 
- Pay Flag with Porosity and Sw Cutoffs. 
- Ability to plot data in a form of Histogram and Scatter Plot.
- Ability to download all plots/histogram/scatterplot in a pdf format. 
- Ability to export the final data (Original LAS data + Formation Evaluation data: VSH, POROSITY, SW)
- Displaying missing data(value) in LAS file as a matrix display

## Some Limitations:
- Only accepting LAS file 2.0.
- Limited bandwith, make sure to select and adjust one feature at a time.
- Make sure to access the website via __https://plotpetrophysics.xyz/__ to access the secured website with SSL certificate. Otherwise, you can still access it via __plotpetrophysics.xyz__ or __www.plotpetrophysics.xyz__ but with no ssl certificate. I am working on making all reroute to https server. Thanks for understanding!

## Exciting Future Plans:
- Adding ability to adjust the plot size, in order to facilitate longer vertical log-type pdf file.
- Adding zonation/ top formation to the plot.
- Adding integrated plot where Triple Combo and Formation Evaluation tracks is available in a single plot.


## Tutorial:
In this tutorial, we will go step by step to create a decent plot based on the preloaded file:

1. Upload your LAS file or use the pre-loaded file:
<img width="1097" alt="CleanShot 2022-01-04 at 17 23 41@2x" src="https://user-images.githubusercontent.com/73975333/148037430-73b3570d-18e7-41f5-a761-aa04af4d1dbd.png">

2. Display the well information based on the LAS file header:
<img width="1097" alt="CleanShot 2022-01-04 at 17 23 41@2x" src="https://user-images.githubusercontent.com/73975333/148037689-3115e6d4-f7ac-48fc-bd62-2f7081057b4b.png">

3. Select the curves based on well information. The triple combo plot typically consist of Gamma-Ray, Resistivity, and Density-Neutron logs:
<img width="1163" alt="CleanShot 2022-01-04 at 17 28 19@2x" src="https://user-images.githubusercontent.com/73975333/148038198-f0a8c524-d7cf-40e9-aadd-267c5bc525f4.png">

4. Adjusting the plot setting such as interval (top and bottom depth), color, scale, and shading:
<img width="995" alt="CleanShot 2022-01-04 at 17 31 13@2x" src="https://user-images.githubusercontent.com/73975333/148038883-349c04aa-dadc-485f-887a-35db5d68d423.png">

<img width="978" alt="CleanShot 2022-01-04 at 17 40 54@2x" src="https://user-images.githubusercontent.com/73975333/148039889-a29a7b56-bef8-446f-a564-7abcc5fd7832.png">

<img width="955" alt="CleanShot 2022-01-04 at 17 41 10@2x" src="https://user-images.githubusercontent.com/73975333/148039919-bc50b5d7-0119-4458-b1d1-0b79490f936a.png">

<img width="979" alt="CleanShot 2022-01-04 at 17 41 04@2x" src="https://user-images.githubusercontent.com/73975333/148039931-cf4b4481-be48-4593-8cdf-fd32754b9644.png">

5. You can do Volume of Shale calculation from Gamma Ray of Density Neutron. You can select porosity from Density, or Density-Neutron Combination

![image](https://user-images.githubusercontent.com/73975333/148176161-75dfd7b7-c33e-48c4-ad15-3416dd67c80d.png)

6. You can calculate Water Resistivity from Salinity, or use your own Rw and calculate the Water Saturation.
![image](https://user-images.githubusercontent.com/73975333/148176252-879ad500-c72c-4228-8aba-880afc9f54e0.png)

7. You can also plot histogram on each curve, or plotting two curves in a scatter plot. 
![image](https://user-images.githubusercontent.com/73975333/148175865-94c984bc-ca94-4d82-b33c-5888f190cd68.png)

![image](https://user-images.githubusercontent.com/73975333/148175885-3d2ca74e-7bba-44f9-9c70-8855167f478e.png)

### Enjoy and Have Fun!




