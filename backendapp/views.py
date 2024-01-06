from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
import json
import ee
import time
from django.shortcuts import render
import math
from django.conf import settings
import numpy as np


def calculate_ndvi(image):
    ndvi = image.normalizedDifference(['B8', 'B4'])
    return image.addBands(ndvi.rename('NDVI'))


def initialize_gee():
    # Initialize Google Earth Engine
    credentials = ee.ServiceAccountCredentials(
        email=settings.GEE_ACCOUNT,
        key_data=settings.GEE_PRIVATE_KEY,
    )
    ee.Initialize(credentials)


def check_gee_initialized():
    return ee.data._credentials is not None


def average_ndvi(request):
    if(request.method == 'POST'):
        if check_gee_initialized():
            print(request.body)
            start_time = time.time()
            postData = json.loads(request.body)
            print(request.body)
            polygon_list = postData['polygonList']
            start_date = postData['startDate']
            end_date = postData['endDate']

            sentinel2 = ee.ImageCollection("COPERNICUS/S2_SR")
            collection = sentinel2 \
                .filterDate(start_date, end_date) \


            average_ndvi_computed_list = []

            for polygon in polygon_list:
                polygon_vertices = polygon['coordinates']

                # Convert the polygon vertices to Earth Engine format
                polygon_coords = [(vertex['lng'], vertex['lat'])
                                  for vertex in polygon_vertices]
                polygon_geometry = ee.Geometry.Polygon([polygon_coords])
                sentinel_collection = collection.filterBounds(polygon_geometry)
                # Map the NDVI calculation function over the collection
                sentinel_with_ndvi = sentinel_collection.map(calculate_ndvi)

                # Select the NDVI band from the processed collection
                ndvi_collection = sentinel_with_ndvi.select('NDVI')
                # Calculate the average NDVI for the selected area and time frame
                average_ndvi = ndvi_collection.mean().reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=polygon_geometry,
                    scale=10
                )

                # Get the average NDVI value
                average_ndvi_value = average_ndvi.get('NDVI').getInfo()
                print(average_ndvi_value)
                average_ndvi_computed_list.append(
                    {'averageNDVI': average_ndvi_value, 'polygonVertices': polygon_vertices})

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Total time taken: {elapsed_time:.2f} seconds")

            return JsonResponse({'computedAverageNDVIList': average_ndvi_computed_list})
        else:
            initialize_gee()
            return JsonResponse({'messgae': 'EE is initialized now'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def point_wise_ndvi(request):
    if request.method == 'POST':
        if check_gee_initialized():
            print(request.body)
            start_time = time.time()
            postData = json.loads(request.body)
            polygon_point_list = postData['polyon_Point_List']
            start_date = postData['startDate']
            end_date = postData['endDate']

            point_ndvi_computed_list = []

            for polygonPoint in polygon_point_list:
                overall_average_ndvi = 0
                polygon_vertices = polygonPoint['polygon']['coordinates']
                points_list = polygonPoint['points']

                # Convert polygon vertices to Earth Engine format
                polygon_coords = [(vertex['lng'], vertex['lat'])
                                  for vertex in polygon_vertices]
                polygon_geometry = ee.Geometry.Polygon([polygon_coords])

                # Load Sentinel-2 imagery
                sentinel2 = ee.ImageCollection("COPERNICUS/S2_SR")
                sentinel_collection = sentinel2 \
                    .filterDate(start_date, end_date) \
                    .filterBounds(polygon_geometry)

                # Create an EE Geometry MultiPoint from the list of points
                points_geometry = ee.Geometry.MultiPoint(
                    [ee.Geometry.Point(point['lng'], point['lat'])
                        for point in points_list]
                )

                # Filter the image collection using the polygon
                filtered_collection = sentinel_collection.filterBounds(
                    points_geometry)

                # Map the NDVI calculation function over the filtered collection
                filtered_with_ndvi = filtered_collection.map(calculate_ndvi)

                # Select the NDVI band from the processed collection
                ndvi_collection = filtered_with_ndvi.select('NDVI')

                # Get NDVI values for each point
                ndvi_values = ndvi_collection.getRegion(
                    points_geometry, scale=10).getInfo()

                # Extract the NDVI values from the response
                header = ndvi_values[0]
                data = ndvi_values[1:]
                ndvi_index = header.index('NDVI')

                calculated_results = []

                for point, row in zip(points_list, data):
                    ndvi = row[ndvi_index]
                    calculated_results.append({
                        'point': point,
                        'ndvi': ndvi+0.05,
                    })
                    overall_average_ndvi = overall_average_ndvi+ndvi
                overall_average_ndvi = overall_average_ndvi/len(points_list)
                print(overall_average_ndvi)
                print("\n\n\n\n")
                point_ndvi_computed_list.append(
                    {'point_ndvi_data': calculated_results, 'polygonVertices': polygon_vertices, 'averageNdvi': overall_average_ndvi})

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Total time taken: {elapsed_time:.2f} seconds")
            return JsonResponse({'computedPointNDVIList': point_ndvi_computed_list})
        else:
            initialize_gee()
            return JsonResponse({'messgae': 'EE is initialized now'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def polygon_point_wise_ndvi(request):
    if request.method == 'POST':
        if check_gee_initialized():
            start_time = time.time()
            postData = json.loads(request.body)

            polygonPoint = postData['polygon']
            start_date = postData['startDate']
            end_date = postData['endDate']

            point_ndvi_computed_list = []
            overall_average_ndvi = 0
            polygon_vertices = polygonPoint['polygon']['coordinates']
            points_list = polygonPoint['points']

            # Convert polygon vertices to Earth Engine format
            polygon_coords = [(vertex['lng'], vertex['lat'])
                              for vertex in polygon_vertices]
            polygon_geometry = ee.Geometry.Polygon([polygon_coords])

            # Load Sentinel-2 imagery
            sentinel2 = ee.ImageCollection("COPERNICUS/S2_SR")
            sentinel_collection = sentinel2 \
                .filterDate(start_date, end_date) \
                .filterBounds(polygon_geometry)

            # Create an EE Geometry MultiPoint from the list of points
            points_geometry = ee.Geometry.MultiPoint(
                [ee.Geometry.Point(point['lng'], point['lat'])
                    for point in points_list]
            )

            # Filter the image collection using the polygon
            filtered_collection = sentinel_collection.filterBounds(
                points_geometry)

            # Map the NDVI calculation function over the filtered collection
            filtered_with_ndvi = filtered_collection.map(calculate_ndvi)

            # Select the NDVI band from the processed collection
            ndvi_collection = filtered_with_ndvi.select('NDVI')

            # Get NDVI values for each point
            ndvi_values = ndvi_collection.getRegion(
                points_geometry, scale=10).getInfo()

            # Extract the NDVI values from the response
            header = ndvi_values[0]
            data = ndvi_values[1:]
            ndvi_index = header.index('NDVI')

            calculated_results = []

            for point, row in zip(points_list, data):
                ndvi = row[ndvi_index]
                ndvi = math.ceil(ndvi * 1000) / 1000
                calculated_results.append({
                    'point': point,
                    'ndvi': ndvi,
                })
                overall_average_ndvi = overall_average_ndvi+ndvi
            overall_average_ndvi = overall_average_ndvi/len(points_list)
            print(overall_average_ndvi)

            calculatedObject = {'point_ndvi_data': calculated_results,
                                'polygonVertices': polygon_vertices, 'averageNdvi': overall_average_ndvi}

            point_ndvi_computed_list.append(calculatedObject)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Total time taken: {elapsed_time:.2f} seconds")
            return JsonResponse({'selectedComputedPointNDVIObject': point_ndvi_computed_list})
        else:
            initialize_gee()
            return JsonResponse({'messgae': 'EE is initialized now'})

    else:
        return JsonResponse({'error': 'Invalid request method'})

def ndvi_heterogeneity_helper_function(ndvi_values):
    # Convert NDVI values to a NumPy array
    ndvi_array = np.array(ndvi_values)
    
    # Calculate the standard deviation of NDVI values
    ndvi_std_dev = np.std(ndvi_array)
    
    return ndvi_std_dev
    
def ndvi_heterogeneity(request):
    if request.method == 'POST':
        if check_gee_initialized():
            start_time = time.time()
            postData = json.loads(request.body)

            polygonPoint = postData['polygon']
            start_date = postData['startDate']
            end_date = postData['endDate']

            point_ndvi_computed_list = []
            ndvi_values_list = []  # List to store NDVI values

            polygon_vertices = polygonPoint['polygon']['coordinates']
            points_list = polygonPoint['points']

            # Convert polygon vertices to Earth Engine format
            polygon_coords = [(vertex['lng'], vertex['lat'])
                              for vertex in polygon_vertices]
            polygon_geometry = ee.Geometry.Polygon([polygon_coords])

            # Load Sentinel-2 imagery
            sentinel2 = ee.ImageCollection("COPERNICUS/S2_SR")
            sentinel_collection = sentinel2 \
                .filterDate(start_date, end_date) \
                .filterBounds(polygon_geometry)

            # Create an EE Geometry MultiPoint from the list of points
            points_geometry = ee.Geometry.MultiPoint(
                [ee.Geometry.Point(point['lng'], point['lat'])
                    for point in points_list]
            )

            # Filter the image collection using the polygon
            filtered_collection = sentinel_collection.filterBounds(
                points_geometry)

            # Map the NDVI calculation function over the filtered collection
            filtered_with_ndvi = filtered_collection.map(calculate_ndvi)

            # Select the NDVI band from the processed collection
            ndvi_collection = filtered_with_ndvi.select('NDVI')

            # Get NDVI values for each point
            ndvi_values = ndvi_collection.getRegion(
                points_geometry, scale=10).getInfo()

            # Extract the NDVI values from the response
            header = ndvi_values[0]
            data = ndvi_values[1:]
            ndvi_index = header.index('NDVI')


            for point, row in zip(points_list, data):
                ndvi = row[ndvi_index]
                ndvi = math.ceil(ndvi * 1000) / 1000
                ndvi_values_list.append(ndvi)  # Append NDVI value to the list

            # Calculate NDVI heterogeneity using the ndvi_heterogeneity_helper_function
            ndvi_heterogeneity_value = ndvi_heterogeneity_helper_function(ndvi_values_list)

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Total time taken: {elapsed_time:.2f} seconds")
            print("NDVI Hetrogeneity Value is: ",ndvi_heterogeneity_value)

            return JsonResponse({'ndviHeterogeneity': ndvi_heterogeneity_value})
        else:
            initialize_gee()
            return JsonResponse({'message': 'EE is initialized now'})

    else:
        return JsonResponse({'error': 'Invalid request method'})




def model_prediction(request):
    if request.method == 'GET':

        
        #------------------------Preprocessing Algorithm------------------------

        #------------------------Input from User------------------------

        input_data = []
        field_coordinates = '[[-98.00721971870774, 26.241158639822448], [-98.00720632414576, 26.240610202970803], [-98.00482512669956, 26.240659246692136], [-98.0048385208193, 26.241203300324152], [-98.00721971870774, 26.241158639822448]]' #coming from user as list and convert it into this
        collection_dates = ['2023-03-01','2023-04-01','2023-05-01','2023-06-01',] #From user coming as month names and convert it to these dates
        area = 3.5649418388421306 #From user coming in hectares and convert to acres




        #------------------------Import satellite imageries------------------------
        sentinel2 = ee.ImageCollection("COPERNICUS/S2_SR");

        USDA_SoilData = ee.ImageCollection("NASA_USDA/HSL/SMAP10KM_soil_moisture");
        #------------------------30m Resolution for elevation------------------------
        NASA_srtm = ee.Image("USGS/SRTMGL1_003");

        #------------------------Modis------------------------
        modis_lai_data = ee.ImageCollection('MODIS/061/MCD15A3H');
        modis_vegetation_data = ee.ImageCollection("MODIS/061/MYD13Q1")
        modis_weather_data = ee.ImageCollection("MODIS/061/MOD21C3")

        #------------------------Load Landsat 8 and 9 image collections------------------------
        landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        landsat9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")


        #------------------------Do preprocessing of satellite imageries------------------------


        landsat8=landsat8.map(calculate_indices_landsat)

        landsat9=landsat9.map(cloud_mask_landsat)
        landsat9=landsat9.map(calculate_indices_landsat)




        # sentinel2 = sentinel2.map(mask_clouds)
        sentinel2 = sentinel2.map(sentinel2_bands_calculations)
        sentinel2 = sentinel2.map(calculate_indices)










        roi = ee.Geometry.Polygon(json.loads(field_coordinates))

        landsat8_error_correction = None

        for i in range(0, len(collection_dates)-1):
            start_date = collection_dates[i]
            end_date = collection_dates[i+1]

            landsat8_flag = True
            usda_flag = True

            sentinel2_data = sentinel2 \
            .filterDate(start_date, end_date) \
            .filterBounds(roi)



            landsat8_data = landsat8 \
            .filterDate(start_date, end_date) \
            .filterBounds(roi)

            if(landsat8_data.size().getInfo()==0):
                landsat8_flag = False





            modis_vegetation = modis_vegetation_data \
            .filterDate(start_date, end_date) \
            .filterBounds(roi)

            modis_weather = modis_weather_data \
            .filterDate(start_date, end_date) \
            .filterBounds(roi)


            USDA_SoilData_data = USDA_SoilData \
            .filterDate(start_date, end_date) \
            .filterBounds(roi)

            if(USDA_SoilData_data.size().getInfo()==0):
                usda_flag = False

            sentinel_2_imagery = sentinel2_data.median().select(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B11', 'B12', 'NDVI', 'EVI', 'GNDVI','SAVI','VCI', 'TVI', 'BI', 'BI2', 'CI', 'CI1', 'SATVI', 'HVSI', 'SOCI', 'ASI', 'BSI', 'MSAVI'])
            modis_vegetation_imagery = modis_vegetation.mosaic().select('NDVI','EVI')
            modis_weather_imagery = modis_weather.first().select('LST_Day','LST_Night')



            elevation = NASA_srtm.clip(roi).log().divide(10).clamp(0, 1).toFloat()



            sentinel_2_stats = sentinel_2_imagery.select(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B11', 'B12', 'NDVI', 'EVI', 'GNDVI','SAVI','VCI', 'TVI', 'BI', 'BI2', 'CI', 'CI1', 'SATVI', 'HVSI', 'SOCI', 'ASI', 'BSI', 'MSAVI']) \
            .addBands(elevation) \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=roi,scale=30)

            modis_vegetation_stats = modis_vegetation_imagery.select(['NDVI','EVI']) \
            .reduceRegion(reducer=ee.Reducer.mean(),geometry=roi,scale=30)

            modis_weather_stats = modis_weather_imagery.select(['LST_Day','LST_Night']) \
            .reduceRegion(reducer=ee.Reducer.mean(),geometry=roi,scale=30)




            indices = sentinel_2_stats.getInfo()
            modis_vegetation_indices = modis_vegetation_stats.getInfo()



            dictionary = {}
            dictionary ['Area'] = area

            dictionary['day time temperature'] = modis_weather_stats.get('LST_Day').getInfo()
            dictionary['night time temperature'] = modis_weather_stats.get('LST_Night').getInfo()

            dictionary['Field Sentinel 2 NDVI'] = indices.get('NDVI')
            dictionary['Field Sentinel 2 EVI'] = indices.get('EVI')
            dictionary['Field Sentinel 2 GNDVI'] = indices.get('GNDVI')
            dictionary['Field Sentinel 2 SAVI'] = indices.get('SAVI')
            dictionary['Field Sentinel 2 B1'] = indices.get('B1')
            dictionary['Field Sentinel 2 B2'] = indices.get('B2')
            dictionary['Field Sentinel 2 B3'] = indices.get('B3')
            dictionary['Field Sentinel 2 B4'] = indices.get('B4')
            dictionary['Field Sentinel 2 B5'] = indices.get('B5')
            dictionary['Field Sentinel 2 B6'] = indices.get('B6')
            dictionary['Field Sentinel 2 B7'] = indices.get('B7')
            dictionary['Field Sentinel 2 B8'] = indices.get('B8')
            dictionary['Field Sentinel 2 B9'] = indices.get('B9')
            dictionary['Field Sentinel 2 B11'] = indices.get('B11')
            dictionary['Field Sentinel 2 B12'] = indices.get('B12')

            dictionary['Field Sentinel 2 VCI'] = indices.get('VCI')
            dictionary['Field Sentinel 2 TVI'] = indices.get('TVI')
            dictionary['Field Sentinel 2 BI'] = indices.get('BI')
            dictionary['Field Sentinel 2 BI2'] = indices.get('BI2')
            dictionary['Field Sentinel 2 CI'] = indices.get('CI')
            dictionary['Field Sentinel 2 CI1'] = indices.get('CI1')
            dictionary['Field Sentinel 2 SATVI'] = indices.get('SATVI')
            dictionary['Field Sentinel 2 HVSI'] = indices.get('HVSI')
            dictionary['Field Sentinel 2 SOCI'] = indices.get('SOCI')
            dictionary['Field Sentinel 2 ASI'] = indices.get('ASI')
            dictionary['Field Sentinel 2 BSI'] = indices.get('BSI')
            dictionary['Field Sentinel 2 MSAVI'] = indices.get('MSAVI')

            dictionary['Field Sentinel 2 Elevation'] = indices.get('elevation')



            if(landsat8_flag):
                landsat8_imagery = landsat8_data.mosaic().select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7','NBR','NDVI','GNDVI','EVI','NDMI','NDWI','NDBI','NDBaI','MNDWI'])
                landsat8_stats = landsat8_imagery.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7','NBR','NDVI','GNDVI','EVI','NDMI','NDWI','NDBI','NDBaI','MNDWI']) \
                .reduceRegion(reducer=ee.Reducer.mean(), geometry=roi,scale=30)
                landsat8_indices = landsat8_stats.getInfo()

                dictionary['Field SR8_B1'] = landsat8_indices.get('SR_B1')
                dictionary['Field SR8_B2'] = landsat8_indices.get('SR_B2')
                dictionary['Field SR8_B3'] = landsat8_indices.get('SR_B3')
                dictionary['Field SR8_B4'] = landsat8_indices.get('SR_B4')
                dictionary['Field SR8_B5'] = landsat8_indices.get('SR_B5')
                dictionary['Field SR8_B6'] = landsat8_indices.get('SR_B6')
                dictionary['Field SR8_B7'] = landsat8_indices.get('SR_B7')
                dictionary['Field NBR_8'] = landsat8_indices.get('NBR')
                dictionary['Field NDMI_8'] = landsat8_indices.get('NDMI')
                dictionary['Field NDWI_8'] = landsat8_indices.get('NDWI')
                dictionary['Field NDBI_8'] = landsat8_indices.get('NDBI')
                dictionary['Field NDBaI_8'] = landsat8_indices.get('NDBaI')
                dictionary['Field MNDWI_8'] = landsat8_indices.get('MNDWI')
                dictionary['Field NDVI_8'] = landsat8_indices.get('NDVI')
                dictionary['Field GNDVI_8'] = landsat8_indices.get('GNDVI')
                dictionary['Field EVI_8'] = landsat8_indices.get('EVI')
                landsat8_error_correction = landsat8_indices
            else:
                print("Landsat Correction took place at: ", start_date, end_date)
                dictionary['Field SR8_B1'] = landsat8_error_correction.get('SR_B1')
                dictionary['Field SR8_B2'] = landsat8_error_correction.get('SR_B2')
                dictionary['Field SR8_B3'] = landsat8_error_correction.get('SR_B3')
                dictionary['Field SR8_B4'] = landsat8_error_correction.get('SR_B4')
                dictionary['Field SR8_B5'] = landsat8_error_correction.get('SR_B5')
                dictionary['Field SR8_B6'] = landsat8_error_correction.get('SR_B6')
                dictionary['Field SR8_B7'] = landsat8_error_correction.get('SR_B7')
                dictionary['Field NBR_8'] = landsat8_error_correction.get('NBR')
                dictionary['Field NDMI_8'] = landsat8_error_correction.get('NDMI')
                dictionary['Field NDWI_8'] = landsat8_error_correction.get('NDWI')
                dictionary['Field NDBI_8'] = landsat8_error_correction.get('NDBI')
                dictionary['Field NDBaI_8'] = landsat8_error_correction.get('NDBaI')
                dictionary['Field MNDWI_8'] = landsat8_error_correction.get('MNDWI')
                dictionary['Field NDVI_8'] = landsat8_error_correction.get('NDVI')
                dictionary['Field GNDVI_8'] = landsat8_error_correction.get('GNDVI')
                dictionary['Field EVI_8'] = landsat8_error_correction.get('EVI')

            landsat8_imagery = landsat8_data.mosaic().select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7','NBR','NDVI','GNDVI','EVI','NDMI','NDWI','NDBI','NDBaI','MNDWI'])
            landsat8_stats = landsat8_imagery.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7','NBR','NDVI','GNDVI','EVI','NDMI','NDWI','NDBI','NDBaI','MNDWI']) \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=roi,scale=30)
            landsat8_indices = landsat8_stats.getInfo()

            dictionary['Field SR8_B1'] = landsat8_indices.get('SR_B1')
            dictionary['Field SR8_B2'] = landsat8_indices.get('SR_B2')
            dictionary['Field SR8_B3'] = landsat8_indices.get('SR_B3')
            dictionary['Field SR8_B4'] = landsat8_indices.get('SR_B4')
            dictionary['Field SR8_B5'] = landsat8_indices.get('SR_B5')
            dictionary['Field SR8_B6'] = landsat8_indices.get('SR_B6')
            dictionary['Field SR8_B7'] = landsat8_indices.get('SR_B7')
            dictionary['Field NBR_8'] = landsat8_indices.get('NBR')
            dictionary['Field NDMI_8'] = landsat8_indices.get('NDMI')
            dictionary['Field NDWI_8'] = landsat8_indices.get('NDWI')
            dictionary['Field NDBI_8'] = landsat8_indices.get('NDBI')
            dictionary['Field NDBaI_8'] = landsat8_indices.get('NDBaI')
            dictionary['Field MNDWI_8'] = landsat8_indices.get('MNDWI')
            dictionary['Field NDVI_8'] = landsat8_indices.get('NDVI')
            dictionary['Field GNDVI_8'] = landsat8_indices.get('GNDVI')
            dictionary['Field EVI_8'] = landsat8_indices.get('EVI')



            dictionary['Field MODIS NDVI'] = normalize_modis_value(modis_vegetation_indices.get('NDVI'))
            dictionary['Field MODIS EVI'] = normalize_modis_value(modis_vegetation_indices.get('EVI'))





            input_data.append(dictionary)

        input_df = pd.DataFrame(input_data)
        input_array = input_df.values
        reshaped_data = input_array.reshape((1, 3, 49))
        print(reshaped_data)
        return JsonResponse({'Data Shape: ':str(reshaped_data)})
        




def sentinel2_bands_calculations(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    gndvi = image.normalizedDifference(['B8', 'B3']).rename('GNDVI')
    evi = image.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
        {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'BLUE': image.select('B2')
        }
    ).rename('EVI')
    red = image.select('B4')  # Red band (Sentinel-2 band 4)
    nir = image.select('B8')  # NIR band (Sentinel-2 band 8)
    savi = nir.subtract(red).divide(nir.add(red).add(0.5)).multiply(1.5).rename('SAVI')
    return image.addBands([ndvi, gndvi, evi, savi])

def mask_clouds(image):
    QA60 = image.select(['QA60'])
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = QA60.bitwiseAnd(cloud_bit_mask).eq(0).And(QA60.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask)

def calculate_indices(image):
    # Calculate VCI (Vegetation Condition Index)
    VCI = image.expression('(NDVI - NDVI_min) / (NDVI_max - NDVI_min) * 100',
                        {'NDVI': image.select('NDVI'),
                            'NDVI_min': 0,
                            'NDVI_max': 0.8}).rename('VCI')

    # Calculate Transformed Vegetation Index (TVI)
    TVI = image.expression('0.5 * (NIR - RED) / (NIR + RED + 0.5)',
                        {'NIR': image.select('B8'),
                            'RED': image.select('B4')}).rename('TVI')

    # Calculate Brightness Index (BI)
    BI = image.expression('sqrt((RED**2) + (NIR**2))',
                        {'RED': image.select('B4'),
                        'NIR': image.select('B8')}).rename('BI')

    # Calculate Second Brightness Index (BI2)
    BI2 = image.expression('(RED + NIR) / 2',
                        {'RED': image.select('B4'),
                            'NIR': image.select('B8')}).rename('BI2')

    # Calculate Color Index (CI)
    CI = image.expression('(NIR / RED) - 1',
                        {'NIR': image.select('B8'),
                        'RED': image.select('B4')}).rename('CI')

    # Calculate Clay Index (CI1)
    CI1 = image.expression('(RED / NIR) - 1',
                        {'RED': image.select('B4'),
                            'NIR': image.select('B8')}).rename('CI1')

    # Calculate SATVI (Soil Adjusted Total Vegetation Index)
    SATVI = image.expression('(NIR - RED - 0.5) / (NIR + RED + 0.5)',
                            {'NIR': image.select('B8'),
                            'RED': image.select('B4')}).rename('SATVI')

    # Calculate HVSI (Hue, Value, and Intensity)
    HVSI = image.expression('sqrt((NIR - RED)**2 + (NIR - GREEN)*(RED - GREEN))',
                            {'NIR': image.select('B8'),
                            'RED': image.select('B4'),
                            'GREEN': image.select('B3')}).rename('HVSI')

    # Calculate SOCI (Soil Organic Carbon Index)
    SOCI = image.expression('(NIR / RED) * (1 + RED - GREEN)',
                            {'NIR': image.select('B8'),
                            'RED': image.select('B4'),
                            'GREEN': image.select('B3')}).rename('SOCI')

    # Calculate ASI (Agricultural Stress Index)
    ASI = image.expression('RED - (GREEN + BLUE) / 2',
                        {'RED': image.select('B4'),
                            'GREEN': image.select('B3'),
                            'BLUE': image.select('B2')}).rename('ASI')

    # Calculate BSI (Bare Soil Index)
    BSI = image.expression('1 - (NIR + 0.05) / (RED + 0.05)',
                        {'NIR': image.select('B8'),
                            'RED': image.select('B4')}).rename('BSI')

    # Calculate MSAVI (Modified Soil Adjusted Vegetation Index)
    MSAVI = image.expression('(2 * NIR + 1 - sqrt((2 * NIR + 1)**2 - 8 * (NIR - RED))) / 2',
                            {'NIR': image.select('B8'),
                            'RED': image.select('B4')}).rename('MSAVI')

    return image.addBands([VCI, TVI, BI, BI2, CI, CI1, SATVI, HVSI, SOCI, ASI, BSI, MSAVI])




def normalize_modis_value(x, min_val=-2000, max_val=10000, new_min=-1, new_max=1):
    normalized_value = ((x - min_val) / (max_val - min_val)) * (new_max - new_min) + new_min
    return normalized_value

#------------------------Function to cloud mask image------------------------
def cloud_mask_landsat(image):
    qa = image.select('QA_PIXEL')
    cloud = 1 << 3
    cirrus = 1 << 9
    mask = qa.bitwiseAnd(cloud).eq(0).And(qa.bitwiseAnd(cirrus).eq(0))
    return image.updateMask(mask)


#------------------------Function to calculate spectral indices------------------------
def calculate_indices_landsat(img):

    ndvi = img.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    gndvi = img.normalizedDifference(['SR_B5', 'SR_B3']).rename('GNDVI')
    evi = img.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
        {
            'NIR': img.select('SR_B5'),
            'RED': img.select('SR_B4'),
            'BLUE': img.select('SR_B2')
        }
    ).rename('EVI')
    nbr = img.normalizedDifference(['SR_B5', 'SR_B7']).rename('NBR')
    ndmi = img.normalizedDifference(['SR_B5', 'SR_B6']).rename('NDMI')
    ndwi = img.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')
    ndbi = img.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI')
    ndbai = img.normalizedDifference(['SR_B6', 'SR_B7']).rename('NDBaI')
    mndwi = img.normalizedDifference(['SR_B3', 'SR_B6']).rename('MNDWI')
    return img.addBands([ndvi,gndvi,evi,nbr, ndmi, ndwi, ndbi, ndbai, mndwi])


