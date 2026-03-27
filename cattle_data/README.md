# USDA Cattle Slaughter Data

## Data Source

This directory contains USDA weekly cattle slaughter data from the Agricultural Marketing Service (AMS).

**Original File**: `Dcowslt-13.xlsx`

## How to Obtain the Data

The raw Excel data file is **not included in this repository** due to file size and licensing considerations.

To obtain the data:

1. **Contact USDA Agricultural Marketing Service (AMS)**
   - Website: https://www.ams.usda.gov/
   - Market News Portal: https://www.ams.usda.gov/market-news

2. **Request the dataset**:
   - U.S. Federally Inspected Cow Slaughter By Region
   - Weekly data, 1984-Present
   - File reference: `Dcowslt-13.xlsx` or equivalent current version

3. **Alternative sources**:
   - Weekly reports: https://www.ams.usda.gov/mnreports/ams_3658.pdf
   - Historical data may need to be requested directly from USDA-AMS

## Processing the Data

Once you have obtained the Excel file:

1. Place `Dcowslt-13.xlsx` in this `cattle_data/` directory
2. Run the processing notebook: `../process_cattle_data.ipynb`
3. This will generate cleaned CSV and Parquet files in this directory

## Output Files

After processing, this directory will contain:

- `cattle_data_clean.csv` - Wide format with all regions and totals
- `cattle_data_clean.parquet` - Compressed parquet version
- `cattle_data_long.csv` - Long format for easier analysis

## Data Description

- **Coverage**: 1984 to present
- **Temporal Resolution**: Weekly
- **Spatial Coverage**: 10 USDA regions covering the continental United States
- **Units**: 1000 head (thousands of cattle)
- **Categories**: Dairy cattle and Beef+Dairy combined

### USDA Regions

- **Region 1 & 2**: CT, ME, NH, VT, MA, RI, NY, NJ
- **Region 3**: DE, MD, PA, WV, VA
- **Region 4**: AL, FL, GA, KY, MS, NC, SC, TN
- **Region 5**: IL, IN, MI, MN, OH, WI
- **Region 6**: AR, LA, NM, OK, TX
- **Region 7**: IA, KS, MO, NE
- **Region 8**: CO, MT, ND, SD, UT, WY
- **Region 9**: AZ, CA, HI, NV
- **Region 10**: AK, ID, OR, WA

## Citation

When using this data, please cite:

> U.S. Department of Agriculture, Agricultural Marketing Service.
> Livestock, Poultry & Grain Market News.
> U.S. Federally Inspected Cow Slaughter By Region, Weekly.
> Retrieved from https://www.ams.usda.gov/

## Notes

- The Excel file contains multiple sheets; processing uses the 'B' sheet with the main data table
- Data includes both reported totals and calculated totals with differences noted
- Some regions may have missing data for certain time periods
