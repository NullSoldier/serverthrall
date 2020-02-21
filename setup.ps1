do
{
	Write-Host "Which do you use to install python packages?"
	Write-Host "Press [1] to use [pip]"
	Write-Host "Press [2] to use [pip3]"
	Write-Host "Press [3] to use [pipenv] (Make sure you're in pipenv shell)"
	$pipmenu = read-host [Enter Selection]
	Switch ($pipmenu) {
		"1" {
				pip install pip==9.0.3
				pip install -r .\requirements.txt
				pip install pip==20.0.2
				pip install -r .\requirements.txt
			}
		"2" {
				pip3 install pip==9.0.3
				pip3 install -r .\requirements.txt
				pip3 install pip==20.0.2
				pip3 install -r .\requirements.txt
			}
		"3" {
				pipenv install pip==9.0.3
				pipenv install -r .\requirements.txt
				pipenv install pip==20.0.2
				pipenv install -r .\requirements.txt
			}
	}
}
until (1..3 -contains $pipmenu)
