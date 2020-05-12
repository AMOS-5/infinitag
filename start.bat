@ECHO OFF
FOR /F "tokens=* USEBACKQ" %%F IN (`where node.exe`) DO (
    SET node_location=%%F
)

FOR /F "tokens=* USEBACKQ" %%F IN (`where py.exe`) DO (
    SET python_location=%%F
)

IF "!node_location!"=="" (
    ECHO No node version was found. Cannot continue
    exit 1
)

if "!python_location!"=="" (
    ECHO Python not found. Cannot continue
    exit 1
)

SET BACKEND_HOST="0.0.0.0"
SET BACKEND_PORT=5000
SET FRONTEND_PORT=4201

SET PRODUCTION=0
SET INSTALL=0

FOR %%A IN (%*) DO (
    IF "%%A"=="/i" SET INSTALL=1
    IF "%%A"=="/p" SET PRODUCTION=1
    IF "%%A"=="/h" (
        ECHO ========= InfiniTag Start Script ===========
        ECHO Arguments:
        ECHO /i install all dependencies for front end and backend. Useful if they have not already been installed
        ECHO /p Start the REST server but only build the front end for production deployment. Useful if you are deploying to a server and don't need the interactive front end.
        ECHO ============================================
    )
)

IF "%INSTALL%"=="1" (
    ECHO Installing Dependencies
    py -m pip install -r requirements.txt
    cd frontend
    npm ci
    cd ../
)

ECHO Starting REST Server...
Start /B "" py app.py --port=%BACKEND_PORT% --host=%BACKEND_HOST% --debug=False

IF "%PRODUCTION%"=="1" (
    ECHO Building for production server
    cd frontend
    node node_modules/@angular/cli/bin/ng build --prod
    cd ../
) ELSE (
    ECHO Starting angular server on port %FRONTEND_PORT%
    cd frontend
    node node_modules/@angular/cli/bin/ng serve --port=%FRONTEND_PORT%

)

PAUSE

