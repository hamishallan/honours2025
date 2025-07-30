% Run ARC Optix Spectrophotometer

% Number of scan averages (#make flexible input in GUI later?)
NrAv = 5;

% Interferogram averaging active (enable only when sufficient light signal is available)
IsIgmAv = false;

% Start scan
iArcspectro.ReadSpectrum(NrAv, IsIgmAv);
%If saturation occurs, print a warning:
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

%Standard normal variate (SNV) normalisation using MATLAB in built function
SNV = normalize(Data.Spectrum);

% Calculate Organic Carbon from normalised spectra and calibration
% coefficients, rounded to 2dp

OC = round(sum(SNV.*Calib_coeff, 'omitnan') + Calib_const, 2)
txt = ['Organic C: ' num2str(OC) ' %'];

% Plot
subplot(2,1,1)
plot(Data.WaveLength*1e18, Data.Spectrum)
title('Raw Reflectance')
text(900,0.9,txt)
ylabel('Reflectance')

subplot(2,1,2)
plot(Data.WaveLength*1e18, SNV)
title('SNV corrected Reflectance')
xlabel('Wavelength, nm')
ylabel('SNV corr. Reflectance')

% write the raw data matrix to csv file with date-time as filename
A = [Data.WaveLength*1e18 Data.Spectrum];
Filename = sprintf('%s.csv', datestr(now,'mm-dd-yyyy HH-MM-SS'));
writematrix(A, Filename);