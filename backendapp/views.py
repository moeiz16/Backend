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
