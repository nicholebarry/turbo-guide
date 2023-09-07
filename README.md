<!-- Project README.md is not documentation. This should contain a high level description of your package. It is what GitHub will display on the front page of your repository. -->
# turbo-guide
Find satellites in astronomy observations

# Satellite Detection
Software which checks the position to satellites within a certain field of view of the sky (Elevation azimuth range or RA and DEC coordinate system) 

## Intent 
- Get positions of satellites.
- Establish location, time and field of view of observer.
- Check if satellite in field of view.

<!-- ## Files -->
<!-- Not necessary if all necessary files exist -->

## Installation
### Developement usage

In terminal:

git clone -b dev-Jason "https://github.com/nicholebarry/turbo-guide.git"

pip install -r requirements.txt

#### In linux environment
python3 ./src/sategazer.py

### Final installation
Use `pip install git+<link>` or download and run `pip install .`

## Usage

### Useful functions
Command line entry points
`get_satellite_position` - Returns coordinates of satellite in desired output.

`set_observer` - Setup the information for the observer 

`check_satellite_position_at_observer` 

`datetime_to_utc`

`utc_to_datetime`

<!-- ### Plotting Utilities -->

## Documentation 
starting point link https://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible

Maybe some papers that mention known locations of satellites

# Author / Contribution
Nichole Barry GitHub: nicholebarry, marcinglowacki, cosmonomad, JasonAhumada

## Citation
If you use this work please include a link to this git repository