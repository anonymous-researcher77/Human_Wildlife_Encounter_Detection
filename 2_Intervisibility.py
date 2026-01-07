#%%# %%

# This Code must be run in a QGIS python environment

#from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsProject
from PyQt5.QtCore import QVariant
import psycopg2
import time
start_time = time.time()
import numpy as np
import ast

from ViewshedAnalysis.algorithms.viewshed_intervisibility import Intervisibility
from ViewshedAnalysis.algorithms.modules import Raster as rst
from ViewshedAnalysis.algorithms.modules import Points as pts
from ViewshedAnalysis.algorithms.modules import visibility as ws

"""
    Checks if paired points in a human-wildlife encounter have intervisibility.

    This function pulls from an SQL encounter_event table and checks intervisibility between all pairs.

    It should be called after creating an encounter_event table but before assigning `id_encounter`.

    Parameters
    ----------
    encounter_event_table : str
        Name of the table containing encounter events, typically created by `create_encounter_events`.

    chamois_height : float
        The estimated height of the animal involved in the encounter.

    human_height : float
        The estimated height of the human involved in the encounter.
    
    vis_column : str
        The name of the column that will be created and store whether there was intervisibility.
    
    DEM_path : str
        The file path to the Digital Elevation Model (DEM) that will be used for testing intervisibility.
        
    db : str
        Name or path of the SQL database containing the encounter events table to be updated.

    Returns
    -------
    None
        This function does not return a value. It updates the encounter events table in the linked database by assigning visibility booleans.
"""

# Uncomment one set of variables and run visibility
# This Code must be run in a QGIS python environment

db       = 'ResRoute'
DEM_path = 'UPDATE THIS FILE PATH see example => /path/to/dem.tif'

run_all = False
batch_size            = 100000

"""
encounter_event_table = 'exp__encounter_event_default'
chamois_height        = 1
human_height          = 1.6
vis_column            = 'vis_grid'
"""

"""
encounter_event_table = 'exp__encounter_event_hda_500'
chamois_height        = 1
human_height          = 1.6
vis_column            = 'vis_grid'
"""

"""
encounter_event_table = 'exp__encounter_event_d_gap_h_none'
chamois_height        = 1
human_height          = 1.6
vis_column            = 'vis_grid'
"""

"""
encounter_event_table = 'exp__encounter_event_d_gap_a_none'
chamois_height        = 1
human_height          = 1.6
vis_column            = 'vis_grid'
"""

"""
encounter_event_table = 'exp__encounter_event_default'
chamois_height        = 0.8
human_height          = 1.6
vis_column            = 'vis_grid_chamois_8_dm'
"""

"""
encounter_event_table = 'exp__encounter_event_default'
chamois_height        = 1.2
human_height          = 1.6
vis_column            = 'vis_grid_chamois_12_dm'
"""

"""
encounter_event_table = 'exp__encounter_event_default'
chamois_height        = 1
human_height          = 2
vis_column            = 'vis_grid_human_2_m'
"""

'---------------------------------------------------------------------------'
def  pairs2 (obs,targets):

    matching_points = []
    for i, (pt1, pt2) in enumerate(zip(obs, targets)):
        obs.pt[pt1]["targets"]={}
        value = targets.pt[pt2]
        id1 = obs.pt[pt1]["id"]        
        id2 = targets.pt[pt2]["id"]
        if id1 == id2:
            obs.pt[pt1]["targets"][pt2]=value
        else:
            print('Ids in pairing do not match')
            break
        x,y = obs.pt[pt1]["pix_coord"]
        x2, y2 = value["pix_coord"]

        if x == x2 and y==y2:
            matching_points.append(id1)
    return matching_points

def pairs2(obs, targets):

    matching_points = []

    # FIX: iterate over point keys
    for pt1, pt2 in zip(obs.pt.keys(), targets.pt.keys()):

        obs.pt[pt1]["targets"] = {}
        value = targets.pt[pt2]

        id1 = obs.pt[pt1]["id"]
        id2 = value["id"]

        if id1 == id2:
            obs.pt[pt1]["targets"][pt2] = value
        else:
            print("Ids in pairing do not match")
            break

        x, y = obs.pt[pt1]["pix_coord"]
        x2, y2 = value["pix_coord"]

        if x == x2 and y == y2:
            matching_points.append(id1)

    return matching_points

def pairs (obs,targets):
     for pt1 in obs.pt:

        id1 = obs.pt[pt1]["id"]        
        x,y = obs.pt[pt1]["pix_coord"]
        
        r = obs.pt[pt1]["radius"] #it's pixelised after take !!

        radius_pix= int(r); r_sq = r**2
        
        max_x, min_x = x + radius_pix, x - radius_pix
        max_y, min_y = y + radius_pix, y - radius_pix

        obs.pt[pt1]["targets"]={}
        
        pt2 = pt1
        value = targets.pt[pt1]

        id2 = targets.pt[pt2]["id"]

        x2, y2 = value["pix_coord"]

        if id1==id2 and x == x2 and y==y2 : 
            obs.pt[pt1]["targets"][pt2]=value
            continue
            
        if min_x <= x2 <= max_x and min_y <= y2 <= max_y:
            if  (x-x2)**2 + (y-y2)**2 <= r_sq:
                obs.pt[pt1]["targets"][pt2]=value

def processAlgorithm_pairs(self, parameters, context, feedback):
    print('Correct Vis')
    raster = self.parameterAsRasterLayer(parameters,self.DEM, context)
    observers = self.parameterAsSource(parameters,self.OBSERVER_POINTS,context)
    targets = self.parameterAsSource(parameters,self.TARGET_POINTS,context)
    write_negative = self.parameterAsBool(parameters,self.WRITE_NEGATIVE,context)

    useEarthCurvature = self.parameterAsBool(parameters,self.USE_CURVATURE,context)
    refraction = self.parameterAsDouble(parameters,self.REFRACTION,context)
    precision = 1#self.parameterAsInt(parameters,self.PRECISION,context)

    
    dem = rst.Raster(raster.source())
   
    o= pts.Points(observers)       
    t= pts.Points(targets)
    
    #setattr(o, 'pairs', pairs)
    #setattr(t, 'pairs', pairs)
    
    required =["observ_hgt", "radius"]

    miss1 = o.test_fields (required)
    miss2 = t.test_fields (required)

    if miss1 or miss2:

        msg = ("\n ********** \n MISSING FIELDS! \n" +
            "\n Missing in observer points: " + ", ".join(miss1) +
            "\n Missing in target points: " + ", ".join(miss2))
           
        raise QgsProcessingException(msg)
             
    o.take(dem.extent, dem.pix)
    t.take(dem.extent, dem.pix)

    if o.count == 0 or t.count == 0:

        msg = ("\n ********** \n ERROR! \n"
            "\n No view points/target points in the chosen area!")
        
        raise QgsProcessingException(msg)
       
    fds = [("Source", QVariant.String, 'string',255),
           ("Target", QVariant.String, 'string',255),
           ("TargetSize", QVariant.Double, 'double',10,3)]

    qfields = QgsFields()
    for f in fds : qfields.append(QgsField(*f))
    
    (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                        qfields,
                        QgsWkbTypes.LineStringZ, #We store Z Geometry now
                        o.crs)
                        
    feedback.setProgressText("*1* Constructing the network")
    
    print('The network is just pairs')
    pairs(o,t)
   
    dem.set_master_window(o.max_radius,
                        curvature =useEarthCurvature,
                        refraction = refraction )
    
    cnt = 0
    
    feedback.setProgressText("*2* Testing visibility")   
    for key, ob in o.pt.items():

        ws.intervisibility(ob, dem, interpolate = precision)
        
        #Get altitude abs for observer
        x,y= ob["pix_coord"]
        radius_pix = dem.radius_pix
        dem.open_window ((x,y))
        data= dem.window
        z_abs =   ob["z"] + data [radius_pix,radius_pix]
        #3D point         
        p1 = QgsPoint(float(ob["x_geog"]), float(ob["y_geog"] ), float(ob["z"]+data [radius_pix,radius_pix]))

        for key, tg in ob["targets"].items():
            
            h = tg["depth"]           
            
            if not write_negative:
                if h<0: continue
            #Get altitude abs for target
            x_tg, y_tg = tg["pix_coord"]  # Target pixel coordinates
            dem.open_window((x_tg, y_tg))
            data= dem.window
            z =   data [radius_pix,radius_pix]
            try: z_targ = tg["z_targ"]
            except : 
                try: z_targ = tg["z"] 
                except : z_targ = 0
            
            p2 = QgsPoint(float(tg["x_geog"]), float(tg["y_geog"] ), float(z+z_targ))

            feat = QgsFeature()
            

            feat.setGeometry(QgsGeometry.fromPolyline([p1, p2]))

            feat.setFields(qfields)
            feat['Source'] = ob["id"]
            feat['Target'] = tg["id"]
            feat['TargetSize'] = float(h) #.                
       
            sink.addFeature(feat, QgsFeatureSink.FastInsert) 
 
        cnt +=1
        feedback.setProgress(int((cnt/o.count) *100))
        if feedback.isCanceled(): return {}

    feedback.setProgressText("*3* Drawing the network")
	

    return {self.OUTPUT: dest_id}

# -----------------------------
# Function to split a layer into batches
# -----------------------------
def split_layer(layer, batch_size):
    features = list(layer.getFeatures())
    total = len(features)
    batches = []

    for i in range(0, total, batch_size):
        batch = features[i:i + batch_size]

        # Create memory layer for batch
        mem = QgsVectorLayer("Point?crs=" + layer.crs().authid(), 
                             f"batch_{i}", "memory")
        prov = mem.dataProvider()
        prov.addAttributes(layer.fields())
        mem.updateFields()
        prov.addFeatures(batch)

        batches.append(mem)

    return batches


# -----------------------------
# Run batched intervisibility
# -----------------------------
def run_intervisibility_in_batches( layerA, 
                                    layerB, 
                                    obs_h_1, 
                                    obs_h_2, 
                                    gridx,
                                    gridy,
                                    gridx_2,
                                    gridy_2,
                                    batch_size=200,
                                    rad = 5000):

    batchesA = split_layer(layerA, batch_size)
    batchesB = split_layer(layerB, batch_size)

    total = len(gridx)
    
    batchs_gridx = []
    batchs_gridy = []
    batchs_gridx_2 = []
    batchs_gridy_2 = []

    # Loop through the lists and create batches
    for i in range(0, total, batch_size):
        batch_gridx = gridx[i:i + batch_size]
        batch_gridy = gridy[i:i + batch_size]
        batch_gridx_2 = gridx_2[i:i + batch_size]
        batch_gridy_2 = gridy_2[i:i + batch_size]

        batchs_gridx.append(batch_gridx)
        batchs_gridy.append(batch_gridy)
        batchs_gridx_2.append(batch_gridx_2)
        batchs_gridy_2.append(batch_gridy_2)
    print('must match')
    print(len(batch_gridx))
    print(len(batchesA))
    print(len(batchesB))
    print('----------')
    results = []



    for i, (bA, bB) in enumerate(zip(batchesA, batchesB)):
        ani_view = processing.run("visibility:createviewpoints", {
            "OBSERVER_POINTS": bA,
            "OBSERVER_ID": 'grid_id',
            "DEM": DEM_path,
            "RADIUS": rad,
            "OBS_HEIGHT": obs_h_1,
            "TARGET_HEIGHT": obs_h_2,
            "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT
        })['OUTPUT']

        human_view = processing.run("visibility:createviewpoints", {
                "OBSERVER_POINTS": bB,
                "OBSERVER_ID": 'grid_id_2',
                "DEM": DEM_path,
                "RADIUS": rad,
                "OBS_HEIGHT": obs_h_2,
                "TARGET_HEIGHT": obs_h_1,
                "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT
            })['OUTPUT']
        print('Batch number : '+str(i))
        print('Human point length : '+ str(human_view.featureCount()))
        print('Animal point length : '+ str(ani_view.featureCount()))

        try:
            visibility_net = processing.run("visibility:intervisibility", {
                    "OBSERVER_POINTS": ani_view,
                    "TARGET_POINTS": human_view,
                    "WRITE_NEGATIVE": True,
                    "DEM": DEM_path,
                    "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT
                })['OUTPUT']
            print('itervis count : '+ str(visibility_net.featureCount()))
        except Exception as e:
            print(f"Inside the loop an error occurred: {e}")
        
        count = visibility_net.featureCount()
        print('intervis count' + str(count))
                
        features = visibility_net.getFeatures()
        type(features)
        
        lst =[]
        lstt = []        
        lst2 = []        

        for feat in features:
            attrs= feat.attributes()

            lst.append(int(attrs[0])-1)
            lstt.append(int(attrs[1])-1)

            #print(attrs)
            if attrs[2] >= 0:
                lst2.append(True)
            else:
                lst2.append(False)
        print(len(lst))
        print(len(lst2))
                
        sorted_truefalse = [None] * len(lst2)
        print('about to create sorted')
        for i_t_f, val in enumerate(lst):            
            sorted_truefalse[val] = lst2[i_t_f]
        print('created sorted')
            
        print('about to zip results')
        print(len(batchs_gridx))
        print(len(batchs_gridx[i]))
        result = list(zip(batchs_gridx[i],batchs_gridy[i],batchs_gridx_2[i],batchs_gridy_2[i], sorted_truefalse))
        print('zipped results')

                
        conn = psycopg2.connect(database=db, user='postgres')
        curs = conn.cursor()


        curs.executemany("""
                    insert into """+str(vis_column)+"""(
                    x_grid,
                    y_grid,
                    x_grid_2,
                    y_grid_2,
                    vis
                )
                    VALUES( %s,
                            %s,
                            %s,
                            %s,
                            %s
                            )
                    """,result)
                
        print('here 11')

        conn.commit()
        curs.close()
        conn.close()
                    
        print('Finished and commited batch ' +str(i))            

def viss(encounter_event_table, 
         height_animal, 
         height_human, 
         db,
         vis_column = 'vis_grid',
         batch_size = 10000):


    ll_x = 924987.5
    ll_y = 6500012.5

    conn = psycopg2.connect(database= db, user='postgres')
    curs = conn.cursor()

    qurry = """\
    create table IF NOT EXISTS """+str(vis_column)+"""(
    x_grid integer,
    y_grid integer,
    x_grid_2 integer,
    y_grid_2 integer,
    vis boolean);
    """

    curs.execute(qurry)


    conn.commit()
    curs.close()
    conn.close()

    conn = psycopg2.connect(database= db, user='postgres')
    curs = conn.cursor()
    
    # Your query to fetch the data
    query = """   
    WITH ttt AS (
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(geom)-"""+ str(ll_y) +""")/25) as y_grid,
            floor((st_x(geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2
        FROM """+ encounter_event_table +"""
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(next_geom)-"""+ str(ll_y) +""")/25) as y_grid,
            floor((st_x(next_geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(next_geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2            
        FROM """+ encounter_event_table +"""
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(geom)-"""+ str(ll_y) +""")/25 )as y_grid,
            floor((st_x(next_geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(next_geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2 
        FROM """+ encounter_event_table +"""
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(next_geom)-"""+ str(ll_y) +""")/25) as y_grid,
            floor((st_x(geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2             
        FROM """+ encounter_event_table +"""
        ORDER BY id_encounter_event, x_grid, y_grid
    )
    SELECT
        1000000*x_grid + y_grid AS grid_id,
        1000000*x_grid_2 + y_grid_2 AS grid_id_2, 
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + """+ str(ll_x) +"""+25/2 AS x_c,
        y_grid * 25 + """+ str(ll_y) +"""+25/2 AS y_c,
        x_grid_2 * 25 + """+ str(ll_x) +"""+25/2 AS x_c2,
        y_grid_2 * 25 + """+ str(ll_y) +"""+25/2 AS y_c2
    FROM ttt
    WHERE NOT EXISTS (
    SELECT 1
    FROM """+str(vis_column)+""" as vg
    WHERE vg.x_grid = ttt.x_grid
      AND vg.y_grid = ttt.y_grid
      AND vg.x_grid_2 = ttt.x_grid_2
      AND vg.y_grid_2 = ttt.y_grid_2
    )
    GROUP BY
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + """+ str(ll_x) +"""+25/2,
        y_grid * 25 + """+ str(ll_y) +"""+25/2,
        x_grid_2 * 25 + """+ str(ll_x) +"""+25/2,
        y_grid_2 * 25 + """+ str(ll_y) +"""+25/2
    """

    # Execute the query
    print(query)
    curs.execute(query)
    print('query ran : ')
    # Create the vector layer (memory layer in EPSG:2154)
    layer = QgsVectorLayer("Point?crs=EPSG:2154", "MemoryLayer_1", "memory")
    layer2 = QgsVectorLayer("Point?crs=EPSG:2154", "MemoryLayer_2", "memory")

    # Add fields to the layer
    fields = [QgsField('id', QVariant.String)]  # Field for storing 'id_1'
    layer.dataProvider().addAttributes(fields)
    layer.updateFields()

    layer2.dataProvider().addAttributes(fields)
    layer2.updateFields()

    QgsProject.instance().addMapLayer(layer)
    QgsProject.instance().addMapLayer(layer2)

    # Access the data provider
    provider = layer.dataProvider()
    provider2 = layer2.dataProvider()
    gridx = []
    gridy = []
    gridx_2 = []
    gridy_2 = []
    lst2 = []
    id_1=[]
    id_2 =[]

    max_dist = 100

    # Loop through the fetched rows and add them as features to the layer
    for row in curs.fetchall():  # Fetch all rows in one go
        id_1.append(int(row[0]))
        id_2.append(int(row[1]))
        gridx.append(int(row[2]))
        gridy.append(int(row[3]))
        gridx_2.append(int(row[4]))
        gridy_2.append(int(row[5]))
        x1, y1 = row[6], row[7]   # observer coords
        x2, y2 = row[8], row[9]   # target coords

        # compute Euclidean distance in meters (EPSG:2154 is meters)
        d = ((x1 - x2)**2 + (y1 - y2)**2)**0.5

        if d > max_dist:
            max_dist = d


        feature = QgsFeature()
        feature2 = QgsFeature()

        # Set the attributes (id_1 is the first column in the result set)
        feature.setAttributes([row[0]])  # row[0] corresponds to 'id_1'
        feature2.setAttributes([row[1]])  # row[0] corresponds to 'id_1'

        # Create the geometry (Point) from x_c and y_c (columns 2 and 3 in the result set)
        point = QgsGeometry.fromPointXY(QgsPointXY(row[6], row[7]))  # x_c and y_c
        point2 = QgsGeometry.fromPointXY(QgsPointXY(row[8], row[9]))  # x_c and y_c
        
        feature.setGeometry(point)
        feature2.setGeometry(point2)

        # Add the feature to the layer
        provider.addFeature(feature)
        provider2.addFeature(feature2)

    # Refresh the layer to update the view
    layer.updateExtents()
    layer2.updateExtents()

    # Ensure the layer is added to the QGIS project
    #QgsProject.instance().addMapLayer(layer)
    #QgsProject.instance().addMapLayer(layer2)

    obs_h_1 = height_animal
    obs_h_2 = height_human
    rad = max_dist+100
    print('About to run intervisibility with rad = ' + str(rad))

    try:
        visibility_net = run_intervisibility_in_batches(layer, 
                                                    layer2,
                                                    obs_h_1,
                                                    obs_h_2,
                                                    gridx,
                                                    gridy,
                                                    gridx_2,
                                                    gridy_2,
                                                    batch_size=batch_size,
                                                    rad = rad)
        
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    
    
    
# Bind the 'pairs' function to the Points class as a method
#setattr(pts, 'pairs', pairs)

# Bind the 'processAlgorithm_pairs' function to the Intervisibility class as a method
setattr(Intervisibility, 'processAlgorithm', processAlgorithm_pairs)

if run_all is False:
    start_time = time.time()
    viss(   encounter_event_table, 
            chamois_height, 
            human_height, 
            db,
            vis_column,
            batch_size)
    print("--- %s seconds ---" % (time.time() - start_time))
elif run_all is True:
  
    start_time_de = time.time()
    viss(   encounter_event_table = 'exp_encounter_event_default',
            height_animal         = 1,
            height_human          = 1.6,
            vis_column            = 'vis_grid',
            db = db,
            batch_size =batch_size)
    print("---For default %s seconds ---" % (time.time() - start_time_de))
    
    start_time_500 = time.time()
    viss(   encounter_event_table = 'exp_encounter_event_hda_500',
            height_animal         = 1,
            height_human          = 1.6,
            vis_column            = 'vis_grid',
            db = db,
            batch_size =batch_size)
    print("---For HDA_radius = 500 %s seconds ---" % (time.time() - start_time_500))
    
    start_time_d_gap_h = time.time()
    viss(   encounter_event_table = 'exp_encounter_event_d_gap_h_none',
            height_animal         = 1,
            height_human          = 1.6,
            vis_column            = 'vis_grid',
            db = db,
            batch_size =batch_size)
    print("---For d_gap_h = None %s seconds ---" % (time.time() - start_time_d_gap_h))
    
    start_time_d_gap_a = time.time()
    viss(   encounter_event_table = 'exp_encounter_event_d_gap_a_none',
            height_animal         = 1,
            height_human          = 1.6,
            vis_column            = 'vis_grid',
            db = db,
            batch_size =batch_size)
    print("---For d_gap_a = None %s seconds ---" % (time.time() - start_time_d_gap_a))
    
    start_time_vis_grid_chamois_8_dm = time.time()
    viss(   encounter_event_table = 'exp_encounter_event_default',
            height_animal        = 0.8,
            height_human          = 1.6,
            vis_column            = 'vis_grid_chamois_8_dm',
            db = db,
            batch_size =batch_size)
    print("---For Chamois height 0.8 m = 0.8 m %s seconds ---" % (time.time() - start_time_vis_grid_chamois_8_dm))
    
    start_time_vis_grid_chamois_12_dm = time.time()
    viss(   encounter_event_table = 'exp_encounter_event_default',
            height_animal         = 0.8,
            height_human          = 1.6,
            vis_column            = 'vis_grid_chamois_12_dm',
            db                    = db,
            batch_size            = batch_size)
    print("---For Chamois height = 1.2 m = 0.8 m %s seconds ---" % (time.time() - start_time_vis_grid_chamois_12_dm))
    
    start_time_vis_grid_human_2_m = time.time()
    viss(   encounter_event_table = 'exp_encounter_event_default',
            height_animal         = 1,
            height_human          = 2,
            vis_column            = 'vis_grid_human_2_m',
            db                    = db,
            batch_size            = batch_size)
    print("---For Chamois height 1.2 m = 0.8 m %s seconds ---" % (time.time() - start_time_vis_grid_human_2_m))
    
       
