
% Initialize DLL - Run and Advance until 'Scan' part of code

% Make sure that this is the installation path of the ARCspectro ROcket
% software
ArcoptixProgramFolder = 'C:\Program Files\ARCoptix\ARCspectro Rocket 2.4.9.18 - x64';

% Add DLL assembly
NET.addAssembly(fullfile(ArcoptixProgramFolder,'ARCsoft.ARCspectroMd.dll'));

% Create interface to spectrometer

iArcspectro = ARCsoft.ARCspectroMd.ARCspectroMd.CreateApiInterface;

% Adjusting gain;

Gain = 'Low'; % Can also be 'Medioum', 'High', 'Extreme'
iArcspectro.Gain = ARCsoft.ARCspectroMd.Gain.(Gain);

% Adjusting and activating apodization

ActiveApoType = 'NortonBeerStrong'; % Can be 'NortonBeerMedium','NortonBeerWeak', 'NortonBeerStrong'
iArcspectro.ActiveApoType = ARCsoft.ARCspectroMd.ApoType.(ActiveApoType);

iArcspectro.ActiveApoIgm = true; % Can also be false

% Load Calibration data from CSV

[inputFile1] = xlsread('Calibration_file.xlsx'); % Read calibration coefficients
Calib_coeff = inputFile1(:,2); % read calibration coefficients into vector
Calib_const = inputFile1(1,3); % read calibration constant into vector
