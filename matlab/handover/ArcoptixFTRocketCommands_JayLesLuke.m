%% Matlab example for FT Rocket checked with DLL version 2.4.9.13

% Initialize DLL - Run and Advance until 'Scan' part of code

% Make sure that this is the installation path of the ARCspectro ROcket
% software
ArcoptixProgramFolder = 'C:\Program Files\ARCoptix\ARCspectro Rocket 2.4.9.18 - x64';

% Add DLL assembly
NET.addAssembly(fullfile(ArcoptixProgramFolder,'ARCsoft.ARCspectroMd.dll'));

% Create interface to spectrometer
% This command works only if you have a single spectrometer connected
% Please contact Arcoptix if you have several spectrometers
iArcspectro = ARCsoft.ARCspectroMd.ARCspectroMd.CreateApiInterface;


%% Adjusting gain

Gain = 'Low'; % Can also be 'Medioum', 'High', 'Extreme'
iArcspectro.Gain = ARCsoft.ARCspectroMd.Gain.(Gain);


%% Adjusting and activating apodization

ActiveApoType = 'NortonBeerStrong'; % Can be 'NortonBeerMedium','NortonBeerWeak', 'NortonBeerStrong'
iArcspectro.ActiveApoType = ARCsoft.ARCspectroMd.ApoType.(ActiveApoType);

iArcspectro.ActiveApoIgm = true; % Can also be false


%% %% START SCANNING - Sample Data (or background etc) - Can just Run Section for this - change file name below

% Number of averages
NrAv = 5;

% Interferogram averaging active (enable only when sufficient light signal is available)
IsIgmAv = false;

% Start scan
iArcspectro.ReadSpectrum(NrAv, IsIgmAv);

% If saturation occurs, print a warning:

if iArcspectro.SaturationRatio>0.9
    warning('Detector saturation');
end

% Read data and sort out relevant indices

% Wevenumber data in [cm-1] (DLL output is in [m-1]
Data.WaveNumber = iArcspectro.Wavenumber.double'/100;

% Wavelength data in [nm]
Data.WaveLength = iArcspectro.Wavelength.double'*1E-9;

% Spectrum
Data.Spectrum = iArcspectro.ApoSpectrum.double';

% Restrict output to spectral range limits of spectrometer

LambdaLims = ...
    [iArcspectro.Configuration.Device.LowerLambda ...
    iArcspectro.Configuration.Device.HigherLambda]*1E-9;

Mask = Data.WaveLength > min(LambdaLims) &  Data.WaveLength < max(LambdaLims);

Data.WaveNumber     = Data.WaveNumber(Mask);
Data.WaveLength     = Data.WaveLength(Mask);
Data.Spectrum       = Data.Spectrum(Mask);

% Plot
plot(Data.WaveLength*1e18, Data.Spectrum)
xlabel('nm')
ylabel('Spectrum [Reflectance]')

% write the matrix to excel sheet
A = [Data.WaveLength*1e18 Data.Spectrum];

%Jaylie file name (change each time relevant part)
writematrix(A,'15Nov2022_1k00_10cm.csv');


% Note do regular backgrounds with white disc 
% Do one every hour or so (add timestamp to background file name)
% make sure the disc and window of integrating sphere is clean (can use ethanol), don't put finger on surface 

