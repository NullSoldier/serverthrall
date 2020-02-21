param(
    [Parameter(Mandatory=$False, Position=0, ValueFromPipeline=$false)]
    [System.String]
    $component
)

Write-Output $component
$component_check = Get-Variable -Name component -Scope Global -ErrorAction SilentlyContinue
Write-Output $component_check

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
	if (test-path ".\bin\serverthrall\build\$build_component") {
		write-host "Removing old build directory at [.\bin\serverthrall\build\$build_component]"
		Remove-Item -Recurse -Force ".\bin\serverthrall\build\$build_component"
	}
	if (-not (test-path ".\bin\serverthrall") ) {
		write-host ".\bin\serverthrall doesn't exist, creating it"
		mkdir ".\bin\serverthrall"|out-null
	}
	#pyinstaller main.py --name "$build_component" --workpath ".\bin\serverthrall\build" --distpath ".\bin\serverthrall\dist" --icon ".\assets\$build_component.ico" --specpath ".\bin\serverthrall" --console --onedir --onefile --noconfirm --clean
	pyinstaller main.py --name "$build_component" --workpath .\bin\serverthrall\build --distpath .\bin\serverthrall\dist --specpath .\bin\serverthrall --console --onedir --onefile --noconfirm --clean
	if (-not (test-path ".\rcedit.exe") ) {
		write-host ".\rcedit.exe doesn't exist, downloading it..."
		Invoke-WebRequest -Uri "https://github.com/electron/rcedit/releases/download/v1.1.1/rcedit-x86.exe" -outfile ".\rcedit.exe"
	}
	.\rcedit.exe ".\bin\serverthrall\dist\$build_component.exe" --set-icon ".\assets\$build_component.ico"
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

switch ( $component )
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
