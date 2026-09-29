
postProcess has been superseded and replaced by the more general foamPostProcess
utility which will be executed instead:

/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  13
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
Build  : 13-18870c24d21c
Exec   : foamPostProcess -latestTime -func fieldMinMax(T)
Date   : Sep 13 2026
Time   : 03:45:44
Host   : "123"
PID    : 14333
I/O    : uncollated
Case   : /media/sf_OpenFOAM_Labs/fast_finish_2026/LR6/nozzleShockFluid
nProcs : 1
sigFpe : Enabling floating point exception trapping (FOAM_SIGFPE).
fileModificationChecking : Monitoring run-time modified files using timeStampMaster (fileModificationSkew 10)
allowSystemOperations : Allowing user-supplied system call operations

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
Create time

Create mesh for time = 0.003



--> FOAM FATAL IO ERROR: 
Cannot find configuration file fieldMinMax

Available configured objects:
119
(
CourantNo
Lambda2
MachNo
PecletNo
Q
Qdot
XiReactionRate
add
adjustTimeStepToChemistry
adjustTimeStepToCombustion
age
bXiProgress
boundaryProbes
cellMax
cellMaxMag
cellMin
cellMinMag
checkMesh
components
cutPlaneSurface
cylindrical
ddt
div
divide
dsmcFields
enstrophy
faceZoneAverage
faceZoneFlowRate
fieldAverage
flowType
forceCoeffsCompressible
forceCoeffsIncompressible
forcesCompressible
forcesIncompressible
functions
grad
graphCell
graphCellFace
graphCutLayerAverage
graphFace
graphLayerAverage
graphPatchCutLayerAverage
graphUniform
interfaceHeight
internalProbes
isoSurface
log
mag
magSqr
massFractions
moleFractions
multiValveEngineState
multiply
particles
patchAverage
patchDifference
patchFlowRate
patchIntegrate
patchSurface
phaseForces
phaseMap
phaseScalarTransport
populationBalanceMoments
populationBalanceSetPhaseSizeDistribution
populationBalanceSetSizeDistribution
populationBalanceSizeDistribution
power
probes
randomise
reactionRates
reconstruct
removeObjects
residuals
scalarTransport
scale
shearStress
specieAdvectiveFlux
specieDiffusiveFlux
specieFlux
specieReactionRates
staticPressureIncompressible
stopAtClockTime
stopAtEmptyClouds
stopAtFile
stopAtTimeStep
streamFunction
streamlinesLine
streamlinesPatch
streamlinesPoints
streamlinesSphere
subtract
surfaceInterpolate
time
timeStep
totalEnthalpy
totalPressureCompressible
totalPressureIncompressible
tr
triSurfaceAverage
triSurfaceDifference
triSurfaceVolumetricFlowRate
turbulenceFields
turbulenceIntensity
uniform
userTimeStep
volAverage
volField
volIntegrate
vorticity
wallBoilingProperties
wallBoilingProperty
wallHeatFlux
wallHeatTransferCoeff
wallShearStress
writeCellCentres
writeCellVolumes
writeObjects
writeVTK
yPlus
)


file: /media/sf_OpenFOAM_Labs/fast_finish_2026/LR6/nozzleShockFluid/system/functions

    From function bool Foam::readConfigFile(const Foam::word&, const Foam::Tuple2<Foam::string, int>&, Foam::dictionary&, const Foam::fileName&, const Foam::word&, const Foam::word&)
    in file db/dictionary/dictionaryIO.C at line 531.

FOAM exiting

