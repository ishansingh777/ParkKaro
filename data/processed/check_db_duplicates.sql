-- READ-ONLY DUPLICATE & PROXIMITY CHECK (Does NOT modify any data)
WITH incoming(external_spot_id, name, city, lon, lat) AS (
    VALUES
        ('osm_way_44280183', 'Indore Parking (osm_way_44280183)', 'Indore', 75.8092622, 22.7288792),
        ('osm_way_191501626', 'Indore Parking (osm_way_191501626)', 'Indore', 75.8971961, 22.7525527),
        ('osm_way_202920191', 'Indore Parking (osm_way_202920191)', 'Indore', 75.8733136, 22.7249642),
        ('osm_way_322425732', 'Indore Parking (osm_way_322425732)', 'Indore', 75.9051442, 22.7521912),
        ('osm_way_322645064', 'Indore Parking (osm_way_322645064)', 'Indore', 75.9001306, 22.7541725),
        ('osm_way_322645065', 'Indore Parking (osm_way_322645065)', 'Indore', 75.9000398, 22.7534361),
        ('osm_way_375229520', 'Indore Parking (osm_way_375229520)', 'Indore', 75.8019655, 22.7276233),
        ('osm_way_700726141', 'Indore Parking (osm_way_700726141)', 'Indore', 75.7913656, 22.6652476),
        ('osm_way_700726142', 'Indore Parking (osm_way_700726142)', 'Indore', 75.7914517, 22.6656623),
        ('osm_way_700726169', 'Indore Parking (osm_way_700726169)', 'Indore', 75.7984053, 22.6682235),
        ('osm_way_770241618', 'Indore Parking (osm_way_770241618)', 'Indore', 75.8689233, 22.7260615),
        ('osm_way_1218177800', 'Indore Parking (osm_way_1218177800)', 'Indore', 75.7964424, 22.5139268),
        ('osm_way_1370087440', 'Indore Parking (osm_way_1370087440)', 'Indore', 75.9228477, 22.5281611),
        ('osm_way_1370088139', 'Indore Parking (osm_way_1370088139)', 'Indore', 75.9247266, 22.5281165),
        ('osm_way_1370088406', 'Indore Parking (osm_way_1370088406)', 'Indore', 75.9235636, 22.5265735),
        ('osm_way_1370088719', 'Indore Parking (osm_way_1370088719)', 'Indore', 75.9201432, 22.5299372),
        ('osm_way_1370089226', 'Indore Parking (osm_way_1370089226)', 'Indore', 75.9264212, 22.5258294),
        ('osm_way_1411656815', 'Indore Parking (osm_way_1411656815)', 'Indore', 75.9277819, 22.7558650),
        ('osm_way_1414327676', 'Indore Parking (osm_way_1414327676)', 'Indore', 75.8988978, 22.7282594),
        ('osm_way_1414327682', 'Indore Parking (osm_way_1414327682)', 'Indore', 75.9283447, 22.7616493),
        ('osm_way_1464595125', 'Indore Parking (osm_way_1464595125)', 'Indore', 75.8372653, 22.7871641),
        ('osm_way_1526718088', 'Indore Parking (osm_way_1526718088)', 'Indore', 75.8469316, 22.7013684),
        ('osm_way_1527217855', 'Indore Parking (osm_way_1527217855)', 'Indore', 75.8746664, 22.7149420),
        ('osm_way_1534546623', 'Indore Parking (osm_way_1534546623)', 'Indore', 75.8687450, 22.7225692),
        ('osm_way_1567032609', 'Indore Parking (osm_way_1567032609)', 'Indore', 75.8532912, 22.8420454),
        ('osm_way_1567032610', 'Indore Parking (osm_way_1567032610)', 'Indore', 75.8525927, 22.8415133),
        ('osm_node_2128648826', 'Indore Parking (osm_node_2128648826)', 'Indore', 75.8732867, 22.7247866),
        ('osm_node_14270121551', 'Indore Parking (osm_node_14270121551)', 'Indore', 75.8535904, 22.8432555),
        ('osm_way_429452128', 'Panaji Parking (osm_way_429452128)', 'Panaji', 73.8031051, 15.4522561),
        ('osm_way_481395155', 'PMC Parking', 'Panaji', 73.8324050, 15.4873506),
        ('osm_way_621256892', 'Panaji Parking (osm_way_621256892)', 'Panaji', 73.8270300, 15.4979609),
        ('osm_way_658699081', 'Panaji Parking (osm_way_658699081)', 'Panaji', 73.8382603, 15.4960337),
        ('osm_way_785029249', 'Panaji Parking (osm_way_785029249)', 'Panaji', 73.8171923, 15.4939615),
        ('osm_way_911221039', 'Panaji Parking (osm_way_911221039)', 'Panaji', 73.8082409, 15.4758493),
        ('osm_way_911228780', 'Panaji Parking (osm_way_911228780)', 'Panaji', 73.8088649, 15.4830723),
        ('osm_way_1019194654', 'Panaji Parking (osm_way_1019194654)', 'Panaji', 73.8018917, 15.4571528),
        ('osm_way_1155877318', 'Panaji Parking (osm_way_1155877318)', 'Panaji', 73.8327203, 15.4995386),
        ('osm_way_1155891465', 'Panaji Parking (osm_way_1155891465)', 'Panaji', 73.8256405, 15.4949922),
        ('osm_way_1156116148', 'Panaji Parking (osm_way_1156116148)', 'Panaji', 73.8337982, 15.4963315),
        ('osm_way_1156650644', 'Inox Parking', 'Panaji', 73.8203902, 15.4984775),
        ('osm_way_1156762020', 'Panaji Parking (osm_way_1156762020)', 'Panaji', 73.8120747, 15.4892922),
        ('osm_way_1156762023', 'Panaji Parking (osm_way_1156762023)', 'Panaji', 73.8147529, 15.4911993),
        ('osm_way_1156779535', 'Panaji Parking (osm_way_1156779535)', 'Panaji', 73.8298340, 15.4972256),
        ('osm_way_1315256439', 'Panaji Parking (osm_way_1315256439)', 'Panaji', 73.8348813, 15.4955201),
        ('osm_way_1323667008', 'Panaji Parking (osm_way_1323667008)', 'Panaji', 73.8211110, 15.4857955),
        ('osm_way_1323689603', 'Panaji Parking (osm_way_1323689603)', 'Panaji', 73.8363209, 15.4989104),
        ('osm_way_1340217084', 'Panaji Parking (osm_way_1340217084)', 'Panaji', 73.8341973, 15.4974313),
        ('osm_way_1340232021', 'Panaji Parking (osm_way_1340232021)', 'Panaji', 73.8346358, 15.4944911),
        ('osm_way_1340240343', 'Panaji Parking (osm_way_1340240343)', 'Panaji', 73.8351827, 15.4973269),
        ('osm_way_1340245545', 'Panaji Parking (osm_way_1340245545)', 'Panaji', 73.8375419, 15.4974195),
        ('osm_way_1340245555', 'Panaji Parking (osm_way_1340245555)', 'Panaji', 73.8369579, 15.4959222),
        ('osm_way_1340334260', 'Panaji Parking (osm_way_1340334260)', 'Panaji', 73.8334247, 15.4973335),
        ('osm_way_1340334264', 'Panaji Parking (osm_way_1340334264)', 'Panaji', 73.8337229, 15.4962553),
        ('osm_way_1340334267', 'Panaji Parking (osm_way_1340334267)', 'Panaji', 73.8336670, 15.4961556),
        ('osm_way_1340334268', 'Panaji Parking (osm_way_1340334268)', 'Panaji', 73.8339283, 15.4963639),
        ('osm_way_1340334271', 'Panaji Parking (osm_way_1340334271)', 'Panaji', 73.8339220, 15.4972524),
        ('osm_way_1411213488', 'Panaji Parking (osm_way_1411213488)', 'Panaji', 73.8284337, 15.5005923),
        ('osm_way_1411213490', 'Panaji Parking (osm_way_1411213490)', 'Panaji', 73.8293450, 15.5004781),
        ('osm_way_1411213491', 'Panaji Parking (osm_way_1411213491)', 'Panaji', 73.8301116, 15.5004905),
        ('osm_way_1411231399', 'Panaji Parking (osm_way_1411231399)', 'Panaji', 73.8255950, 15.5014768),
        ('osm_way_1428214009', 'Panaji Parking (osm_way_1428214009)', 'Panaji', 73.8269489, 15.4883221),
        ('osm_way_1447421638', 'Dona Paula Parking', 'Panaji', 73.8041282, 15.4581042),
        ('osm_way_1459841763', 'Basement Paid Parking', 'Panaji', 73.8221796, 15.4989540),
        ('osm_way_1459841780', 'Panaji Parking (osm_way_1459841780)', 'Panaji', 73.8141551, 15.4888067),
        ('osm_way_1489499511', 'Panaji Parking (osm_way_1489499511)', 'Panaji', 73.8308050, 15.4960355),
        ('osm_way_1502797180', 'Panaji Parking (osm_way_1502797180)', 'Panaji', 73.8263752, 15.5012518),
        ('osm_way_1524898189', 'Panaji Parking (osm_way_1524898189)', 'Panaji', 73.8156929, 15.4885811),
        ('osm_way_1545339136', 'Panaji Parking (osm_way_1545339136)', 'Panaji', 73.8288482, 15.5006672),
        ('osm_way_1547916158', 'Panaji Parking (osm_way_1547916158)', 'Panaji', 73.8353144, 15.4964346),
        ('osm_way_1547916160', 'Panaji Parking (osm_way_1547916160)', 'Panaji', 73.8348194, 15.4959586),
        ('osm_way_1547918937', 'Panaji Parking (osm_way_1547918937)', 'Panaji', 73.8347859, 15.4975101),
        ('osm_way_1569607331', 'Panaji Parking (osm_way_1569607331)', 'Panaji', 73.8319700, 15.4973733),
        ('osm_way_1569607332', 'Panaji Parking (osm_way_1569607332)', 'Panaji', 73.8316648, 15.4974611),
        ('osm_way_1571653613', 'Panaji Parking (osm_way_1571653613)', 'Panaji', 73.8282224, 15.4988716),
        ('osm_way_1575252810', 'Bus Parking', 'Panaji', 73.8363921, 15.4952625),
        ('osm_way_1578216355', 'Panaji Parking (osm_way_1578216355)', 'Panaji', 73.8096932, 15.4878030),
        ('osm_way_1578223390', 'Panaji Parking (osm_way_1578223390)', 'Panaji', 73.8117498, 15.4893567)
)
SELECT
    CASE
        WHEN p.external_spot_id = i.external_spot_id THEN 'EXACT_ID_MATCH'
        ELSE 'NEARBY_WITHIN_30M'
    END AS conflict_type,
    i.external_spot_id AS incoming_external_id,
    i.name AS incoming_name,
    i.city AS incoming_city,
    p.id AS existing_db_id,
    p.name AS existing_name,
    p.city AS existing_city,
    p.external_spot_id AS existing_external_id,
    ROUND(
        ST_Distance(
            p.location,
            ST_SetSRID(ST_MakePoint(i.lon, i.lat), 4326)::geography
        )::numeric,
        2
    ) AS distance_meters
FROM incoming i
JOIN public.parking_spots p
  ON p.external_spot_id = i.external_spot_id
  OR ST_DWithin(
      p.location,
      ST_SetSRID(ST_MakePoint(i.lon, i.lat), 4326)::geography,
      30
  )
ORDER BY conflict_type, distance_meters;
