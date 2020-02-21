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
		rm  -r -fo ".\bin\serverthrall\build\$build_component"
	}
	if (-not (test-path ".\bin\serverthrall") ) {
		write-host ".\bin\serverthrall doesn't exist, creating it"
		mkdir ".\bin\serverthrall"|out-null
	}
	pyinstaller main.py --name "$build_component" --workpath .\\bin\\serverthrall\\build --distpath .\\bin\\serverthrall\\dist --specpath .\\bin\\serverthrall --icon .\\serverthrall.ico --console --onedir --onefile --noconfirm --clean
}

function Build-Vendor-steamcmd {
	if (test-path ".\bin\serverthrall\dist\vendor\steamcmd") {
		write-host "Removing steamcmd vendor directory at [.\bin\serverthrall\dist\vendor\steamcmd]"
		rm -r -fo ".\bin\serverthrall\dist\vendor\steamcmd"
	}
	write-host "Creating .\bin\serverthrall\dist\vendor\steamcmd"
	mkdir ".\bin\serverthrall\dist\vendor\steamcmd"|out-null
	cp .\vendor\steamcmd\steamcmd.exe .\bin\serverthrall\dist\vendor\steamcmd\steamcmd.exe
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
