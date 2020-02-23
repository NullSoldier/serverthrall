param(
    [Parameter(Mandatory=$False, Position=0, ValueFromPipeline=$false)]
    [System.String]
    $component
)

$srcdir = ((Resolve-Path .\).Path)

if (!$component)
{
	do
	{
		Write-Host "Press [1] to build [serverthrall.exe]"
		Write-Host "Press [2] to build [updater.exe]"
		Write-Host "Press [3] to build both [serverthrall.exe] and [updater.exe]"
		$componentmenu = read-host [Enter Selection]
		Switch ($componentmenu) {
			"1" {
					$component = "serverthrall"
				}
			"2" {
					$component = "updater"
				}
			"3" {
					$component = "all"
				}
		}
	}
	until (1..3 -contains $componentmenu)
}

function Build-App {
	Param ($build_component)
	switch ($build_component)
    {
        serverthrall
        {
            $build_PyFile = "main.py"
        }
        updater
        {
            $build_PyFile = "updater.py"   
        }
    }
    if (test-path ".\bin\serverthrall\build\$build_component") {
		write-host "Removing old build directory at [.\bin\serverthrall\build\$build_component]"
		#Remove-Item -Recurse -Force ".\bin\serverthrall\build\$build_component"
	}
	if (-not (test-path ".\bin\serverthrall") ) {
		write-host ".\bin\serverthrall doesn't exist, creating it"
		mkdir ".\bin\serverthrall"|out-null
	}
    
    pyi-makespec "$build_PyFile" --name "$build_component" --specpath .\bin\serverthrall --onedir --onefile --console --hidden-import pkg_resources.py2_warn
    $pyvenv = ((python -c "import os; print(os.environ['VIRTUAL_ENV'])"))
    $pyvenv = "$pyvenv\Lib\site-packages"
    $pyvenv = [regex]::escape($pyvenv)
    $srcdirex = [regex]::escape($srcdir)
    (Get-Content -path .\bin\serverthrall\$build_component.spec -Raw) -replace "pathex=\['\.\\\\bin\\\\serverthrall']","pathex=['.\\bin\\serverthrall','$pyvenv']" | Set-Content -Path .\bin\serverthrall\$build_component.spec
    (Get-Content -path .\bin\serverthrall\$build_component.spec -Raw) -replace "console=True \)","console=True, icon='$srcdirex\\assets\\$build_component.ico' )" | Set-Content -Path .\bin\serverthrall\$build_component.spec
    pyinstaller ".\bin\serverthrall\$build_component.spec" --name "$build_component" --workpath ".\bin\serverthrall\build" --distpath ".\bin\serverthrall\dist" --console --onedir --onefile --noconfirm --clean
}

function Build-Vendor-steamcmd {
	if (test-path ".\bin\serverthrall\dist\vendor\steamcmd") {
		write-host "Removing steamcmd vendor directory at [.\bin\serverthrall\dist\vendor\steamcmd]"
		Remove-Item -Recurse -Force ".\bin\serverthrall\dist\vendor\steamcmd"
	}
	write-host "Creating .\bin\serverthrall\dist\vendor\steamcmd"
	mkdir ".\bin\serverthrall\dist\vendor\steamcmd"|out-null
    Invoke-WebRequest -Uri "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip" -outfile ".\bin\serverthrall\dist\vendor\steamcmd\steamcmd.zip"
    expand-archive -path ".\bin\serverthrall\dist\vendor\steamcmd\steamcmd.zip" -destinationpath ".\bin\serverthrall\dist\vendor\steamcmd"
    Remove-Item -Recurse -Force ".\bin\serverthrall\dist\vendor\steamcmd\steamcmd.zip"
}

switch ($component)
    {
        serverthrall
        {
            Build-App -build_component serverthrall
			Build-Vendor-steamcmd
        }
        updater
        {
            Build-App -build_component updater
        }
        all
        {
            Build-App -build_component serverthrall
			Build-App -build_component updater
			Build-Vendor-steamcmd
        }
    }
    