"""
ParkKaro Sign Knowledge Base - Easy Understanding Edition
Simple, plain, everyday language for Indian traffic and parking signs.
Includes:
1. What the sign means in simple words
2. What you should do right now
3. Common Misconception / Wrong Meaning (लोग क्या गलत समझते हैं)
4. Whether you can park your vehicle here
5. Challan / Fine under Motor Vehicles Act
"""

SIGN_KNOWLEDGE = {
    # 1. PARKING & RESTRICTIONS
    "NO_PARKING": {
        "name": "No Parking",
        "category": "Strict Rule (Mandatory)",
        "meaning": "You cannot park your car or bike here. Leaving your vehicle unattended is not allowed.",
        "wrong_meaning": "Thinking: 'I can park for 10-15 minutes if I turn on hazard flashers (parking blinkers).' — WRONG! Hazard lights do NOT give legal permission to park in a No-Parking zone.",
        "driver_action": "Do not leave your vehicle here. If you only need to drop someone off, do it quickly with the engine running and move away immediately.",
        "parking_impact": "❌ NO PARKING. This is an active tow-away zone monitored by traffic police.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine + Towing charges (Crane fee)."
    },
    "NO_STOPPING_OR_STANDING": {
        "name": "No Stopping (No Halting)",
        "category": "Strict Rule (Mandatory)",
        "meaning": "You cannot stop your vehicle here at all—not even for 5 seconds to drop or pick up someone! Stopping here blocks fast traffic.",
        "wrong_meaning": "Thinking: 'I can stop for 30 seconds to pick up a friend or answer a phone call.' — WRONG! In a No-Stopping zone, halting even for 5 seconds is illegal and gets towed.",
        "driver_action": "Keep driving continuously. Do not brake or halt your car/bike on this road or flyover.",
        "parking_impact": "❌ ZERO STOPPING ZONE. Your car or bike will be towed away immediately.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 to ₹1,500 fine + Immediate vehicle towing."
    },
    "NO_ENTRY": {
        "name": "No Entry (One-Way)",
        "category": "Strict Rule (Mandatory)",
        "meaning": "Vehicles are NOT allowed to enter this road from this direction. It is either a one-way street or a closed road.",
        "wrong_meaning": "Thinking: 'It's only for heavy trucks or during peak hours; I can enter if no police is watching.' — WRONG! Entering is strictly banned 24/7 for all vehicles.",
        "driver_action": "Do not enter this road. Turn around and take an alternate street.",
        "parking_impact": "❌ NO PARKING. Driving or parking in a No-Entry zone is illegal.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 to ₹5,000 fine for dangerous wrong-way driving."
    },
    "ALL_MOTOR_VEHICLE_PROHIBITED": {
        "name": "No Cars or Bikes Allowed",
        "category": "Vehicle Restriction",
        "meaning": "No motorized vehicles (cars, motorcycles, scooters, autos, trucks) are allowed here. This area is reserved only for people walking.",
        "wrong_meaning": "Thinking: 'Only cars and trucks are banned; two-wheelers can sneak in.' — WRONG! Bikes and scooters are motorized vehicles and are completely banned.",
        "driver_action": "Do not ride or drive into this street. Park your vehicle in a public parking lot outside and walk in.",
        "parking_impact": "❌ NO MOTOR VEHICLE PARKING. Only pedestrians allowed.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine under Motor Vehicles Act."
    },
    "STOP": {
        "name": "Stop Sign",
        "category": "Important Junction Rule",
        "meaning": "You must bring your vehicle to a complete halt before the white line. Look both ways for crossing vehicles, and move only when the road is completely clear.",
        "wrong_meaning": "Thinking: 'Slowing down to 5 km/h without fully stopping is okay.' — WRONG! You must come to a complete zero-speed stop before moving ahead.",
        "driver_action": "Press your brakes and stop fully. Never leave your vehicle parked near a stop line.",
        "parking_impact": "❌ NO PARKING within 15 meters of any intersection stop line.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for jumping a Stop sign or blocking the road."
    },
    "GIVE_WAY": {
        "name": "Give Way (Let Other Cars Go First)",
        "category": "Merging Rule",
        "meaning": "Vehicles on the main road have priority. Slow down and let them pass first before you join the main road.",
        "wrong_meaning": "Thinking: 'The upside-down triangle means I have the right to go first.' — WRONG! It means YOU must yield and let other cars pass first.",
        "driver_action": "Slow down, check traffic, and wait for a safe gap before entering the road.",
        "parking_impact": "❌ NO PARKING along road corners or merging lanes.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine."
    },
    "STRAIGHT_PROHIBITED": {
        "name": "No Going Straight",
        "category": "Direction Restriction",
        "meaning": "You cannot drive straight ahead. You must turn either left or right.",
        "wrong_meaning": "Thinking: 'I can go straight if the road ahead looks empty.' — WRONG! The road ahead might be one-way against you or blocked by construction.",
        "driver_action": "Do not drive straight. Choose a safe left or right turn.",
        "parking_impact": "❌ NO PARKING along this lane.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine."
    },
    "RIGHT_TURN_PROHIBITED": {
        "name": "No Right Turn",
        "category": "Turn Restriction",
        "meaning": "Turning right is strictly banned at this intersection to avoid traffic jams and accidents.",
        "wrong_meaning": "Thinking: 'I can turn right if there are no oncoming vehicles right now.' — WRONG! Right turn is banned because crossing opposite lanes causes major accidents.",
        "driver_action": "Do not turn right. Continue straight or turn left if permitted.",
        "parking_impact": "❌ NO PARKING near this intersection corner.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine."
    },
    "LEFT_TURN_PROHIBITED": {
        "name": "No Left Turn",
        "category": "Turn Restriction",
        "meaning": "Turning left is banned here, usually because the left side is a one-way road coming towards you.",
        "wrong_meaning": "Thinking: 'Left turns are always free in India.' — WRONG! Free left turn does NOT apply when this prohibited sign is posted.",
        "driver_action": "Do not turn left. Go straight or turn right as allowed.",
        "parking_impact": "❌ NO PARKING near the corner.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine."
    },
    "U_TURN_PROHIBITED": {
        "name": "No U-Turn (यू-टर्न मना है)",
        "category": "Strict Median Restriction",
        "meaning": "You cannot turn your car around (take a U-turn) at this divider gap. Turning here is dangerous and strictly prohibited.",
        "wrong_meaning": "Thinking: 'I can take a quick U-turn if the road looks clear for a second.' — WRONG! U-turns here cause fatal blind-spot crashes with fast oncoming vehicles.",
        "driver_action": "Do not attempt a U-turn here. Continue straight to the next designated roundabout or legal divider cut.",
        "parking_impact": "❌ NO PARKING inside or near the divider opening or median cut.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for dangerous illegal U-turn under Motor Vehicles Act."
    },
    "U_TURN": {
        "name": "U-Turn Permitted (यू-टर्न ले सकते हैं)",
        "category": "Permitted Turn Direction",
        "meaning": "You are legally permitted to turn your vehicle around (take a U-turn) here into the opposite direction.",
        "wrong_meaning": "Thinking: 'I can park or stop in the U-turn lane to drop someone.' — WRONG! Stopping in a U-turn pocket blocks turning cars and causes serious rear-end crashes.",
        "driver_action": "Slow down, turn on your right indicator, give way to oncoming cars, and turn smoothly when safe.",
        "parking_impact": "❌ NO PARKING in or near the U-turn opening. Keep the turning lane 100% clear.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine for parking or obstructing a U-turn lane."
    },
    "NOT_DETECTED": {
        "name": "No Traffic Sign Recognized (साइन नहीं पहचाना गया)",
        "category": "Unverified Frame",
        "meaning": "The camera could not find a clear Indian traffic or parking sign in this image.",
        "wrong_meaning": "Thinking: 'If the scanner didn't detect a sign, I can park freely anywhere.' — WRONG! Many streets have curb markings (yellow curb = strict tow-away) or remote CCTV enforcement without physical boards.",
        "driver_action": "Hold the sign closer and straight in front of your camera, ensure good lighting, or upload a clear front-facing photo.",
        "parking_impact": "⚠️ Cannot verify parking rules automatically. Check roadside boards and yellow curb paint manually before parking.",
        "rule_type": "UNKNOWN",
        "penalty": "Standard fines apply (₹500 - ₹1,000) if parked in an unverified tow-away zone."
    },
    "OVERTAKING_PROHIBITED": {
        "name": "No Overtaking",
        "category": "Safety Rule",
        "meaning": "Do not overtake other cars on this road. The road is narrow, has blind curves, or is an accident-prone bridge.",
        "wrong_meaning": "Thinking: 'I can overtake slow autos, bikes, or tractors.' — WRONG! You cannot overtake ANY vehicle on this narrow or curved road.",
        "driver_action": "Stay in your line behind the vehicle in front of you. Be patient.",
        "parking_impact": "❌ NO PARKING. Road is too narrow; parked cars will cause massive jams.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 to ₹2,000 fine for dangerous driving."
    },
    "HORN_PROHIBITED": {
        "name": "Silence Zone (No Honking)",
        "category": "Silence Zone",
        "meaning": "Do not blow your horn here! You are near a hospital with patients, a school with students, or a court.",
        "wrong_meaning": "Thinking: 'I can honk lightly if someone is walking slowly in front of me.' — WRONG! Honking is strictly banned near ICUs, hospitals, and courtrooms.",
        "driver_action": "Drive silently without pressing the horn. If parking, don't use loud car alarms or rev your engine.",
        "parking_impact": "✅ Parking allowed in marked parking spaces, but keep the area quiet.",
        "rule_type": "ALLOWED",
        "penalty": "₹1,000 fine for unnecessary honking."
    },

    # 2. COMPULSORY DIRECTIONS (MUST FOLLOW)
    "COMPULSARY_AHEAD": {
        "name": "Go Straight Only",
        "category": "Mandatory Direction",
        "meaning": "You MUST drive straight ahead only. You are not allowed to turn left or right.",
        "wrong_meaning": "Thinking: 'I can turn if my Google Maps route says to turn.' — WRONG! Road signs override GPS; you must proceed straight only.",
        "driver_action": "Keep driving straight in your lane. Do not stop to block cars behind you.",
        "parking_impact": "❌ NO PARKING on through-traffic lanes.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 fine for disobeying traffic signs."
    },
    "COMPULSARY_AHEAD_OR_TURN_LEFT": {
        "name": "Go Straight or Turn Left",
        "category": "Mandatory Direction",
        "meaning": "You can either go straight or turn left at this junction. Turning right or taking a U-turn is strictly forbidden.",
        "wrong_meaning": "Thinking: 'I can turn right or take a U-turn if no police is watching.' — WRONG! Turning right here goes against incoming traffic or into closed lanes.",
        "driver_action": "Pick either the straight or left lane. Do not park near this corner as it blocks turning traffic.",
        "parking_impact": "⚠️ Keep the turning corner clear. Park only in designated roadside parking slots.",
        "rule_type": "ALLOWED",
        "penalty": "₹500 fine for blocking the turning lane."
    },
    "COMPULSARY_AHEAD_OR_TURN_RIGHT": {
        "name": "Go Straight or Turn Right",
        "category": "Mandatory Direction",
        "meaning": "You can either go straight or turn right. Turning left is not allowed.",
        "wrong_meaning": "Thinking: 'I can take a left turn if I indicate with my blinker.' — WRONG! Left turns are completely forbidden at this junction.",
        "driver_action": "Drive straight or take the right turn. Do not stop in the middle of the road.",
        "parking_impact": "⚠️ Keep turning lane clear of parked vehicles.",
        "rule_type": "ALLOWED",
        "penalty": "₹500 fine for blocking traffic."
    },
    "COMPULSARY_KEEP_LEFT": {
        "name": "Keep Left of Divider",
        "category": "Road Divider Rule",
        "meaning": "Drive on the LEFT side of the road divider, island, or obstacle in front of you.",
        "wrong_meaning": "Thinking: 'I can choose either side of the divider.' — WRONG! Going right of this divider puts you directly into oncoming traffic.",
        "driver_action": "Steer left of the barrier. Never drive on the right side against oncoming traffic.",
        "parking_impact": "❌ NO PARKING near or on the road divider.",
        "rule_type": "ALLOWED",
        "penalty": "₹500 fine for wrong-side driving."
    },
    "COMPULSARY_KEEP_RIGHT": {
        "name": "Keep Right of Divider",
        "category": "Road Divider Rule",
        "meaning": "Drive on the RIGHT side of the road barrier or road work.",
        "wrong_meaning": "Thinking: 'I can pass on the left if there is room.' — WRONG! Left side is blocked or hazardous.",
        "driver_action": "Follow the right path as directed.",
        "parking_impact": "❌ NO PARKING near the barrier.",
        "rule_type": "ALLOWED",
        "penalty": "₹500 fine."
    },
    "COMPULSARY_TURN_LEFT": {
        "name": "Must Turn Left",
        "category": "Mandatory Direction",
        "meaning": "You MUST turn left here. You cannot go straight or turn right.",
        "wrong_meaning": "Thinking: 'This is just a recommended shortcut.' — WRONG! Blue circular signs are legally MANDATORY.",
        "driver_action": "Turn your vehicle to the left immediately.",
        "parking_impact": "❌ NO PARKING within 10 meters of the turning corner.",
        "rule_type": "ALLOWED",
        "penalty": "₹500 fine for wrong direction."
    },
    "COMPULSARY_TURN_RIGHT": {
        "name": "Must Turn Right",
        "category": "Mandatory Direction",
        "meaning": "You MUST turn right here. You cannot go straight or turn left.",
        "wrong_meaning": "Thinking: 'I can go straight if the road ahead looks open.' — WRONG! Straight road is blocked or restricted.",
        "driver_action": "Turn right into the road.",
        "parking_impact": "❌ Keep the turning corner free of parked vehicles.",
        "rule_type": "ALLOWED",
        "penalty": "₹500 fine."
    },
    "COMPULSARY_SOUND_HORN": {
        "name": "Blow Horn (Blind Curve Ahead)",
        "category": "Mountain & Curve Safety",
        "meaning": "You MUST blow your horn before taking this turn! There is a blind curve or hill bend where other drivers cannot see you coming.",
        "wrong_meaning": "Thinking: 'It has a horn picture so it means Silence Zone / Don't Honk.' — WRONG! Blue circle means it is COMPULSORY to blow your horn for safety.",
        "driver_action": "Honk your horn twice and slow down before entering the curve.",
        "parking_impact": "❌ EXTREMELY DANGEROUS TO PARK HERE. Never park on a blind turn.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine for hazardous parking on turns."
    },
    "ROUNDABOUT": {
        "name": "Roundabout (Chauraha / Gol Chakkar)",
        "category": "Junction Rule",
        "meaning": "Circular junction ahead. Vehicles already inside the circle have the right of way. Move in a clockwise circle.",
        "wrong_meaning": "Thinking: 'Vehicles entering the circle have priority.' — WRONG! Vehicles ALREADY INSIDE have first right of way; you must wait before entering.",
        "driver_action": "Slow down, let cars already inside pass, then enter smoothly in clockwise direction.",
        "parking_impact": "❌ STRICTLY NO PARKING inside or within 25 meters of any roundabout.",
        "rule_type": "NO_PARKING",
        "penalty": "Immediate towing and ₹1,000 fine for blocking a roundabout."
    },

    # 3. SPEED LIMITS
    "SPEED_LIMIT_5": {"name": "Speed Limit: 5 km/h", "category": "Crawl Speed Zone", "meaning": "Drive at walking speed (5 km/h). This is inside parking lots, hospital gates, or residential societies.", "wrong_meaning": "Thinking: 'Nobody monitors speed inside parking gates.' — WRONG! Speed bumps and boom barriers enforce this limit.", "driver_action": "Keep foot gently on brake; drive very slowly.", "parking_impact": "✅ Parking bays usually available nearby.", "rule_type": "ALLOWED", "penalty": "Over-speeding fine ₹1,000."},
    "SPEED_LIMIT_15": {"name": "Speed Limit: 15 km/h", "category": "Slow Speed Zone", "meaning": "Maximum speed is 15 km/h in narrow residential alleys or school compounds.", "wrong_meaning": "Thinking: 'I can accelerate if the street is empty.' — WRONG! Kids or stray animals can run out suddenly.", "driver_action": "Drive at low speed and watch out for people.", "parking_impact": "✅ Check for local street parking lines.", "rule_type": "ALLOWED", "penalty": "Over-speeding fine ₹1,000."},
    "SPEED_LIMIT_20": {"name": "Speed Limit: 20 km/h", "category": "Market Speed Zone", "meaning": "Do not drive faster than 20 km/h. High pedestrian movement in this market area.", "wrong_meaning": "Thinking: '20 km/h is too slow, I can do 35-40.' — WRONG! Market crowds make emergency braking at 40 impossible.", "driver_action": "Maintain slow speed and watch out for pedestrians.", "parking_impact": "💰 Look for municipal Pay & Park slots.", "rule_type": "ALLOWED", "penalty": "Over-speeding fine ₹1,000."},
    "SPEED_LIMIT_30": {"name": "Speed Limit: 30 km/h", "category": "City Speed Zone", "meaning": "Maximum speed is 30 km/h in city residential neighborhoods.", "wrong_meaning": "Thinking: 'Speed limits are only for cars, not two-wheelers.' — WRONG! Speed limits apply equally to all bikes and cars.", "driver_action": "Keep your speed at or under 30 km/h.", "parking_impact": "✅ Street parking allowed where marked.", "rule_type": "ALLOWED", "penalty": "₹1,000 online speed challan."},
    "SPEED_LIMIT_40": {"name": "Speed Limit: 40 km/h", "category": "City Main Road", "meaning": "Speed limit is 40 km/h on main city roads and market avenues.", "wrong_meaning": "Thinking: 'I can drive 50 km/h without getting a challan.' — WRONG! Automated speed radar cameras trigger online challans even at 43 km/h.", "driver_action": "Stay within 40 km/h. Speed cameras may be active.", "parking_impact": "⚠️ Park only in white-lined parking spaces.", "rule_type": "ALLOWED", "penalty": "₹1,000 to ₹2,000 speed camera challan."},
    "SPEED_LIMIT_50": {"name": "Speed Limit: 50 km/h", "category": "Ring Road Speed Limit", "meaning": "Maximum speed is 50 km/h on city arterial corridors and ring roads.", "wrong_meaning": "Thinking: 'This is the minimum speed.' — WRONG! This is the absolute MAXIMUM legal speed allowed.", "driver_action": "Keep your speedometer under 50 km/h.", "parking_impact": "⚠️ Roadside parking restricted on high-speed roads.", "rule_type": "ALLOWED", "penalty": "₹2,000 online speed camera challan."},
    "SPEED_LIMIT_60": {"name": "Speed Limit: 60 km/h", "category": "Highway Corridor", "meaning": "Speed limit is 60 km/h on outer bypass and express roads.", "wrong_meaning": "Thinking: 'Highways have no speed limits.' — WRONG! Speed interceptor vans monitor bypass roads actively.", "driver_action": "Drive steadily at safe speed.", "parking_impact": "❌ No parking on main lanes. Use service roads.", "rule_type": "NO_PARKING", "penalty": "₹2,000 speed fine."},
    "SPEED_LIMIT_70": {"name": "Speed Limit: 70 km/h", "category": "Four-Lane Highway", "meaning": "Highway speed limit of 70 km/h for four-lane divided highways.", "wrong_meaning": "Thinking: 'Right lane has no speed limit.' — WRONG! The limit applies to ALL lanes.", "driver_action": "Maintain highway discipline. Keep left unless overtaking.", "parking_impact": "❌ NO PARKING on the highway shoulder.", "rule_type": "NO_PARKING", "penalty": "₹2,000 fine."},
    "SPEED_LIMIT_80": {"name": "Speed Limit: 80 km/h", "category": "Expressway Speed Limit", "meaning": "Fast expressway speed limit of 80 km/h.", "wrong_meaning": "Thinking: 'I can pull over on the expressway shoulder to stretch or take a call.' — WRONG! Stopping on expressway shoulders without breakdown causes fatal pileups.", "driver_action": "High speed lane. Maintain safe distance from cars in front.", "parking_impact": "❌ STRICTLY NO PARKING on expressway. Emergency breakdown only.", "rule_type": "NO_PARKING", "penalty": "₹2,000 to ₹4,000 fine for stopping on an expressway."},

    # 4. VEHICLE TYPE PROHIBITIONS
    "TRUCK_PROHIBITED": {
        "name": "No Heavy Trucks",
        "category": "Heavy Vehicle Ban",
        "meaning": "Large commercial trucks cannot enter this road. Cars, two-wheelers, and autos are allowed.",
        "wrong_meaning": "Thinking: 'Small delivery trucks or tempos can enter.' — WRONG! All commercial goods vehicles are barred during restricted hours.",
        "driver_action": "Truck drivers must take the outer bypass. Cars may proceed.",
        "parking_impact": "✅ Cars and bikes can park in designated bays.",
        "rule_type": "ALLOWED",
        "penalty": "₹2,000 fine for truck entry."
    },
    "CYCLE_PROHIBITED": {
        "name": "No Bicycles",
        "category": "Cycle Restriction",
        "meaning": "Bicycles are banned on this high-speed flyover or expressway for safety.",
        "wrong_meaning": "Thinking: 'Electric cycles or sports bicycles can go.' — WRONG! All non-motorized and slow cycles are banned.",
        "driver_action": "Cyclists must use service roads.",
        "parking_impact": "Motor corridor; standard parking rules apply.",
        "rule_type": "ALLOWED",
        "penalty": "Fine for cycle entry."
    },
    "PEDESTRIAN_PROHIBITED": {
        "name": "No Walking (Pedestrians Banned)",
        "category": "Pedestrian Safety",
        "meaning": "People are NOT allowed to walk on this high-speed flyover, tunnel, or expressway.",
        "wrong_meaning": "Thinking: 'I can walk along the side crash barrier.' — WRONG! Walking on high-speed flyovers is strictly illegal and dangerous.",
        "driver_action": "Watch for fast traffic. No footpaths available.",
        "parking_impact": "❌ Strictly No Parking or stopping here.",
        "rule_type": "NO_PARKING",
        "penalty": "Fine for stopping on restricted flyover."
    },

    # 5. WARNINGS & CAUTIONS
    "PEDESTRIAN_CROSSING": {
        "name": "Zebra Crossing (People Crossing)",
        "category": "Pedestrian Priority",
        "meaning": "People cross the street here on white zebra stripes. People walking have the first right of way by law.",
        "wrong_meaning": "Thinking: 'Pedestrians should wait until all cars pass.' — WRONG! Under Indian Motor Vehicles Act, pedestrians on a zebra crossing have 100% legal right of way; drivers must stop.",
        "driver_action": "Slow down and stop your car before the white stripes to let people walk across safely.",
        "parking_impact": "❌ NEVER PARK ON A ZEBRA CROSSING or within 10 meters of it.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine for blocking a zebra crossing."
    },
    "SCHOOL_AHEAD": {
        "name": "School Zone Ahead",
        "category": "Child Safety Zone",
        "meaning": "There is a school nearby! Young children may cross the road or run out from between parked cars unexpectedly.",
        "wrong_meaning": "Thinking: 'This only applies during morning 8 AM and afternoon 2 PM.' — WRONG! Kids participate in sports and evening activities; drive slowly throughout the day.",
        "driver_action": "Slow down to 20 km/h, keep your eyes on the sides of the road, and be ready to brake.",
        "parking_impact": "❌ DO NOT PARK in front of the school gate during school opening/closing hours.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for reckless driving or blocking school gates."
    },
    "MEN_AT_WORK": {
        "name": "Road Work in Progress",
        "category": "Construction Warning",
        "meaning": "Laborers and machines are actively digging or repairing the road ahead.",
        "wrong_meaning": "Thinking: 'Work is paused if no workers are standing on the road.' — WRONG! Open trenches, gravel, and wet tar remain dangerous 24 hours.",
        "driver_action": "Slow down, follow yellow barricades, and do not try to speed past construction trucks.",
        "parking_impact": "❌ NO PARKING in active road work zones. Machinery will tow or damage your car.",
        "rule_type": "NO_PARKING",
        "penalty": "Immediate towing for work obstruction."
    },
    "NARROW_ROAD_AHEAD": {
        "name": "Road Becomes Narrow",
        "category": "Road Warning",
        "meaning": "The wide road you are driving on shrinks into a tighter, narrower street ahead.",
        "wrong_meaning": "Thinking: 'I should accelerate to overtake cars before the road gets narrow.' — WRONG! Racing to merge is the #1 cause of head-on crashes.",
        "driver_action": "Slow down and merge gently into a single lane without overtaking.",
        "parking_impact": "❌ NO PARKING along narrow bottle-necks.",
        "rule_type": "NO_PARKING",
        "penalty": "Fine for creating a traffic choke point."
    },
    "NARROW_BRIDGE": {
        "name": "Narrow Bridge Ahead",
        "category": "Bridge Warning",
        "meaning": "Approaching bridge is narrow. Two big cars or buses cannot pass at the same time.",
        "wrong_meaning": "Thinking: 'Both cars can squeeze through if we drive slowly.' — WRONG! Only one vehicle can safely pass at a time; yield to the vehicle closer to the bridge.",
        "driver_action": "Slow down and let oncoming vehicles on the bridge cross first before entering.",
        "parking_impact": "❌ NEVER PARK on or near a bridge under any circumstances.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,500 fine + Immediate towing."
    },
    "TRAFFIC_SIGNAL": {
        "name": "Traffic Signal Lights Ahead",
        "category": "Signal Alert",
        "meaning": "Traffic lights ahead. Be prepared to slow down for yellow and stop for red.",
        "wrong_meaning": "Thinking: 'Yellow light means step on the gas to beat the red light.' — WRONG! Yellow means prepare to come to a smooth, safe stop.",
        "driver_action": "Look ahead at the light; do not speed up to beat the yellow light.",
        "parking_impact": "❌ NO PARKING within 15 meters of any traffic signal.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for red light jump or signal obstruction."
    },
    "HUMP_OR_ROUGH_ROAD": {
        "name": "Speed Breaker / Bumpy Road",
        "category": "Road Surface Alert",
        "meaning": "Speed breaker (bump) or rough potholes ahead on the road.",
        "wrong_meaning": "Thinking: 'Driving fast over bumps makes them feel smoother.' — WRONG! It destroys car shock absorbers, alignment, and tyres.",
        "driver_action": "Press your brakes smoothly to slow down so your car underbody does not scrape.",
        "parking_impact": "Do not park right on top of speed breakers.",
        "rule_type": "ALLOWED",
        "penalty": "Drive carefully."
    },
    "SLIPPERY_ROAD": {
        "name": "Slippery Road (Skid Risk)",
        "category": "Hazard Warning",
        "meaning": "The road ahead is slippery due to rain, oil, loose sand, or water. Tyres may lose grip easily.",
        "wrong_meaning": "Thinking: 'My car has ABS and traction control, so it won't slip.' — WRONG! Modern electronics cannot defy physics on oil slicks or wet mud.",
        "driver_action": "Drive slowly, avoid sudden hard braking, and do not make sharp steering turns.",
        "parking_impact": "Hazardous road edge; park only on solid, dry ground.",
        "rule_type": "NO_PARKING",
        "penalty": "Accident risk warning."
    },
    "FALLING_ROCKS": {
        "name": "Falling Rocks (Hill Danger)",
        "category": "Mountain Danger",
        "meaning": "Mountain road where loose stones or boulders can fall from hill slopes onto your car.",
        "wrong_meaning": "Thinking: 'I can park on the shoulder to click photos of the valley.' — WRONG! Loose boulders can crush vehicles without warning.",
        "driver_action": "Drive through without stopping. Do not stop to take selfies.",
        "parking_impact": "❌ NEVER PARK UNDER CLIFFS OR ROCKFALL ZONES.",
        "rule_type": "NO_PARKING",
        "penalty": "High safety risk of rock damage."
    },
    "GAP_IN_MEDIAN": {
        "name": "Divider Cut (Median Opening)",
        "category": "Divider Cut Alert",
        "meaning": "There is a gap in the center road divider where cars may turn or cross in front of you.",
        "wrong_meaning": "Thinking: 'Cars in the divider will always wait for me.' — WRONG! Impatient drivers frequently nose out; slow down and stay alert.",
        "driver_action": "Slow down and watch out for vehicles suddenly sticking their nose out from the median.",
        "parking_impact": "❌ NO PARKING in the divider opening.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for blocking a median cut."
    },
    "GUARDED_LEVEL_CROSSING": {
        "name": "Railway Gate Ahead (With Barrier)",
        "category": "Railway Alert",
        "meaning": "Railway crossing with gate barriers ahead. Trains pass frequently.",
        "wrong_meaning": "Thinking: 'I can duck or drive under the railway gate while it is coming down.' — WRONG! Highly illegal, fatal, and leads to immediate arrest under Railway Act.",
        "driver_action": "Stop behind the white line when the red light flashes or gate is closing. Never sneak under a closing gate.",
        "parking_impact": "❌ STRICTLY NO PARKING within 30 meters of railway tracks.",
        "rule_type": "NO_PARKING",
        "penalty": "Heavy fine and jail under Railway Act for gate violations."
    },
    "UNGUARDED_LEVEL_CROSSING": {
        "name": "Railway Crossing Ahead (No Gate)",
        "category": "Extreme Danger",
        "meaning": "Open railway tracks with NO GATE and NO WATCHMAN! Trains travel at high speed and cannot stop.",
        "wrong_meaning": "Thinking: 'I can hear a train horn from far away so I don't need to stop.' — WRONG! Modern electric trains approach silently at 110+ km/h.",
        "driver_action": "Stop completely, roll down your window, look left and right, listen for train horn, and cross only when 100% clear.",
        "parking_impact": "❌ NEVER PARK NEAR TRAIN TRACKS.",
        "rule_type": "NO_PARKING",
        "penalty": "Severe danger to life."
    },
    "RESTRICTION_ENDS": {
        "name": "All Restrictions End",
        "category": "Info Sign",
        "meaning": "Previous road restrictions (like speed limits or no overtaking) have ended here. Standard highway rules now apply.",
        "wrong_meaning": "Thinking: 'There are no rules now; I can speed as fast as I want.' — WRONG! Standard default state highway and national speed limits still apply.",
        "driver_action": "Resume normal safe driving.",
        "parking_impact": "Standard parking rules apply.",
        "rule_type": "ALLOWED",
        "penalty": "None."
    },
    "AXLE_LOAD_LIMIT": {
        "name": "Axle Load Limit (धुरी भार सीमा)",
        "category": "Weight Restriction",
        "meaning": "Vehicles with axle weight higher than the shown number cannot cross. Heavy trucks can break this bridge or road.",
        "wrong_meaning": "Thinking: 'My total truck weight is fine, so axle weight doesn't matter.' — WRONG! Bridge structural strength is calculated per single axle, not overall vehicle weight.",
        "driver_action": "Check your vehicle's laden axle weight. Heavy multi-axle trucks must use the designated bypass.",
        "parking_impact": "❌ Heavy vehicles cannot park or wait on this weak bridge or road.",
        "rule_type": "NO_PARKING",
        "penalty": "₹20,000 fine + ₹2,000 per excess tonne for overloaded vehicles."
    },
    "BARRIER_AHEAD": {
        "name": "Toll / Checkpost Barrier Ahead (टोल या पुलिस बैरियर)",
        "category": "Mandatory Halt",
        "meaning": "There is a police checkpoint, toll plaza, or security boom barrier ahead where you must stop.",
        "wrong_meaning": "Thinking: 'I can zoom past if the boom barrier looks open.' — WRONG! Barrier sensors drop the pole onto your car, causing severe vehicle damage and police intercept.",
        "driver_action": "Slow down to a stop, prepare your Fastag/documents, and wait for clearance.",
        "parking_impact": "❌ STRICT NO PARKING within 100 meters of a toll barrier or checkpost.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for lane blocking or barrier skipping."
    },
    "BULLOCK_AND_HANDCART_PROHIBITED": {
        "name": "No Bullocks or Handcarts (बैलगाड़ी और हाथठेला मना)",
        "category": "Slow Vehicle Ban",
        "meaning": "Slow-moving animal carts and hand-pushed vending carts are strictly banned on this fast highway or flyover.",
        "wrong_meaning": "Thinking: 'Street vendors can push their carts along the shoulder lane.' — WRONG! Non-motorized slow carts cause fatal rear-end highway crashes.",
        "driver_action": "Carts must use service roads or city bypasses.",
        "parking_impact": "❌ No carts or loading/unloading on highway shoulders.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 fine and cart impoundment."
    },
    "BULLOCK_PROHIBITED": {
        "name": "No Bullock Carts Allowed (बैलगाड़ी मना है)",
        "category": "Animal Cart Ban",
        "meaning": "Animal-drawn carts (bullock, horse, camel carts) are forbidden on this expressway or city artery.",
        "wrong_meaning": "Thinking: 'I can ride a cart during night hours when traffic is low.' — WRONG! Unlit animal carts at night are the leading cause of highway fatalities.",
        "driver_action": "Use interior rural connecting roads.",
        "parking_impact": "❌ No tying animals or parking carts on road shoulders.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 fine under Police Act."
    },
    "CATTLE": {
        "name": "Cattle / Livestock Crossing (मवेशी crossing)",
        "category": "Animal Hazard Alert",
        "meaning": "Cows, buffaloes, or goats frequently wander or cross the road here. Villagers herd cattle across this stretch.",
        "wrong_meaning": "Thinking: 'Cows will move away if I honk loudly.' — WRONG! Sudden loud honking startles cattle and causes them to charge into oncoming cars.",
        "driver_action": "Slow down immediately, do not honk aggressively, and let animals clear the road.",
        "parking_impact": "⚠️ Avoid parking near cattle sheds or grazing borders where animals can scratch vehicles.",
        "rule_type": "ALLOWED",
        "penalty": "Accident liability if driving recklessly through animal zones."
    },
    "COMPULSARY_CYCLE_TRACK": {
        "name": "Mandatory Cycle Lane (केवल साइकिल ट्रैक)",
        "category": "Designated Lane",
        "meaning": "This lane is strictly reserved for bicycles. Bicyclists must use this lane, and motor vehicles cannot enter.",
        "wrong_meaning": "Thinking: 'Two-wheelers and scooters can use the cycle lane during traffic jams.' — WRONG! Riding motorbikes on cycle tracks is illegal and heavily fined.",
        "driver_action": "Keep your car or motorbike out of this lane. Leave it completely free for cyclists.",
        "parking_impact": "❌ STRICT TOW-AWAY ZONE. Parking any motor vehicle in a cycle track leads to instant towing.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 to ₹1,500 fine for driving or parking in dedicated cycle lanes."
    },
    "COMPULSARY_MINIMUM_SPEED": {
        "name": "Minimum Speed Limit (न्यूनतम गति सीमा)",
        "category": "Expressway Flow Rule",
        "meaning": "You must drive at or faster than this speed (e.g. 50 km/h). Driving too slowly on high-speed expressways causes rear-end pileups.",
        "wrong_meaning": "Thinking: 'Driving very slowly in the center lane is always safer.' — WRONG! Driving below the minimum speed creates a moving roadblock.",
        "driver_action": "Maintain your speed at or above the posted number. If your car is malfunctioning, move to the emergency breakdown shoulder.",
        "parking_impact": "❌ ABSOLUTELY ZERO STOPPING OR PARKING on minimum speed expressway lanes.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 to ₹2,000 fine for obstructing expressway traffic flow."
    },
    "COMPULSARY_TURN_LEFT_AHEAD": {
        "name": "Compulsory Turn Left Ahead (आगे अनिवार्य बायाँ मोड़)",
        "category": "Mandatory Turn",
        "meaning": "The road ahead forces all traffic to turn left. You cannot continue straight or turn right.",
        "wrong_meaning": "Thinking: 'I can go straight if the road looks open.' — WRONG! The straight road is closed, under construction, or one-way in reverse.",
        "driver_action": "Indicate left in advance, get into the left lane, and make the turn.",
        "parking_impact": "❌ NO PARKING along the turn pocket or curb.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine for disobeying mandatory lane directions."
    },
    "COMPULSARY_TURN_RIGHT_AHEAD": {
        "name": "Compulsory Turn Right Ahead (आगे अनिवार्य दायाँ मोड़)",
        "category": "Mandatory Turn",
        "meaning": "You are required by law to turn right at the upcoming intersection.",
        "wrong_meaning": "Thinking: 'This is just a suggested route from municipal planning.' — WRONG! Blue circular signs are mandatory traffic laws in India.",
        "driver_action": "Indicate right early, merge into the right-turn bay, and execute the turn.",
        "parking_impact": "❌ NO PARKING in right-turn approach lanes.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 to ₹1,000 fine for lane discipline violation."
    },
    "CROSS_ROAD": {
        "name": "Four-Way Cross Intersection Ahead (चौराहा आगे है)",
        "category": "Intersection Caution",
        "meaning": "Major 4-way crossroads ahead where vehicles cross from left, right, and straight.",
        "wrong_meaning": "Thinking: 'The biggest road always gets to speed through without slowing down.' — WRONG! Cross-traffic may misjudge your speed. Always slow down before junctions.",
        "driver_action": "Slow down, glance in all 4 directions, yield to vehicles from your right, and proceed cautiously.",
        "parking_impact": "❌ STRICT NO PARKING within 15 meters of any four-way intersection.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for obstructing crossroad traffic."
    },
    "CYCLE_CROSSING": {
        "name": "Bicycle Crossing Ahead (साइकिल crossing)",
        "category": "Cyclist Safety Alert",
        "meaning": "Bicycles frequently cross the highway or street here from connecting tracks or villages.",
        "wrong_meaning": "Thinking: 'Cyclists have to stop and wait for cars every time.' — WRONG! Drivers must yield to cyclists at marked cycle crossings.",
        "driver_action": "Slow down, scan both sides of the road for bicycles, and be prepared to stop.",
        "parking_impact": "❌ NO PARKING within 10 meters of a bicycle crossing.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 fine for blocking a designated crossing."
    },
    "DANGEROUS_DIP": {
        "name": "Deep Dip / Depression Ahead (खतरनाक गड्ढा / ढलान)",
        "category": "Road Surface Hazard",
        "meaning": "A steep, sudden dip or storm drain ditch in the road ahead. Hitting this at speed will smash your bumper and ruin suspension.",
        "wrong_meaning": "Thinking: 'My SUV has high ground clearance so I don't need to slow down.' — WRONG! Sudden dips launch vehicles airborne and cause loss of steering control.",
        "driver_action": "Brake firmly and drive through the dip at crawling speed (10-15 km/h).",
        "parking_impact": "❌ NEVER PARK INSIDE A ROAD DIP. Water collects here during rain, flooding parked cars.",
        "rule_type": "NO_PARKING",
        "penalty": "Severe vehicle underbody damage risk."
    },
    "DIRECTION": {
        "name": "Direction Guide Sign (दिशा सूचक बोर्ड)",
        "category": "Navigational Guide",
        "meaning": "Points you toward cities, airports, ring roads, or key destination exits.",
        "wrong_meaning": "Thinking: 'I can reverse back on the expressway if I miss my exit.' — WRONG! Reversing on highways causes catastrophic high-speed fatal collisions.",
        "driver_action": "Read the sign early, choose your lane well before the exit divider, and take the turn smoothly.",
        "parking_impact": "❌ NO PARKING in front of directional signage boards.",
        "rule_type": "ALLOWED",
        "penalty": "Fine for hazardous reversing or lane-hopping."
    },
    "FALLING_ROCKS": {
        "name": "Landslide / Falling Rocks Zone (चट्टान गिरने का खतरा)",
        "category": "Mountain Hazard",
        "meaning": "Steep mountain hillside prone to falling boulders and landslides, especially during monsoon rains.",
        "wrong_meaning": "Thinking: 'I can park on the cliff edge to take mountain photos.' — WRONG! Loose boulders can crush stationary vehicles without warning.",
        "driver_action": "Drive through continuously without lingering. Do not stop to take selfies.",
        "parking_impact": "❌ ZERO PARKING PERMITTED UNDER CLIFFS OR ROCKFALL ZONES.",
        "rule_type": "NO_PARKING",
        "penalty": "Extreme safety risk to life and vehicle."
    },
    "FERRY": {
        "name": "Ferry / River Boat Crossing (नाव / नौका घाट)",
        "category": "Waterway Warning",
        "meaning": "The road ends at a riverbank or boat ferry loading dock ahead.",
        "wrong_meaning": "Thinking: 'The road continues across on a shallow bridge.' — WRONG! The road literally ends in deep water. Speeding ahead will submerge your car.",
        "driver_action": "Brake early, slow down to a crawl, and follow ferry attendant instructions.",
        "parking_impact": "❌ Park only in designated ferry terminal waiting bays. Never park on the boat slipway.",
        "rule_type": "ALLOWED",
        "penalty": "Fine for blocking ferry boarding ramps."
    },
    "HANDCART_PROHIBITED": {
        "name": "Handcarts Prohibited (हाथठेला मना है)",
        "category": "Slow Traffic Restriction",
        "meaning": "Hand-pushed commercial carts and fruit/vegetable carts are not allowed on this flyover or road.",
        "wrong_meaning": "Thinking: 'Small handcarts can push against traffic.' — WRONG! Handcarts in fast traffic cause sudden lane swerves and accidents.",
        "driver_action": "Push cart along designated service lanes or internal market streets.",
        "parking_impact": "❌ No cart parking on the main road carriageway.",
        "rule_type": "NO_PARKING",
        "penalty": "Cart impoundment and fine."
    },
    "HEIGHT_LIMIT": {
        "name": "Height Restriction Limit (अधिकतम ऊंचाई सीमा)",
        "category": "Overhead Clearance",
        "meaning": "Vehicles taller than the indicated height (e.g., 3.5m) cannot pass under the upcoming railway bridge, underpass, or metro girder.",
        "wrong_meaning": "Thinking: 'My truck is only 2 inches taller, it will squeeze through.' — WRONG! Hitting a concrete bridge crushes truck roofs and stops trains.",
        "driver_action": "If your vehicle is taller than the marked limit, stop and take the designated bypass route.",
        "parking_impact": "❌ NO PARKING in front of height barrier gantries.",
        "rule_type": "NO_PARKING",
        "penalty": "₹5,000 to ₹10,000 fine + structural damage repair costs."
    },
    "LEFT_HAIR_PIN_BEND": {
        "name": "Hairpin Bend to the Left (बायाँ हेयरपिन मोड़)",
        "category": "Ghat Mountain Curve",
        "meaning": "Extreme 180-degree U-shaped mountain curve twisting back to the left ahead. Complete blind spot.",
        "wrong_meaning": "Thinking: 'I can overtake a slow truck on the hairpin curve.' — WRONG! Mountain buses and trucks swing wide across both lanes on hairpin bends.",
        "driver_action": "Shift to 1st or 2nd gear, blow your horn loud, stay on the extreme left, and turn slowly.",
        "parking_impact": "❌ NEVER PARK ON OR NEAR A HAIRPIN BEND. Vehicles cannot see you around the cliff.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,500 fine for dangerous parking on mountain curves."
    },
    "LEFT_HAND_CURVE": {
        "name": "Gentle Left Curve Ahead (बायाँ मोड़ आगे है)",
        "category": "Road Alignment",
        "meaning": "Road bends gently to the left ahead. Visibility is limited around the curve.",
        "wrong_meaning": "Thinking: 'I don't need to slow down on gentle curves.' — WRONG! Centrifugal force causes cars to drift outward into oncoming lanes if speeding.",
        "driver_action": "Ease off the accelerator, keep both hands on the wheel, and maintain lane discipline.",
        "parking_impact": "❌ Never park on the outer or inner shoulder of a road curve.",
        "rule_type": "ALLOWED",
        "penalty": "Fine for improper parking on curved lanes."
    },
    "LEFT_REVERSE_BEND": {
        "name": "Reverse S-Curve to Left (ज़िगज़ैग बायाँ मोड़)",
        "category": "Double Curve Warning",
        "meaning": "Double sharp turn ahead: first bends left, then immediately bends right (S-bend).",
        "wrong_meaning": "Thinking: 'Once I clear the first turn, I can accelerate hard.' — WRONG! The second turn curves in the opposite direction immediately.",
        "driver_action": "Slow down before entering the first turn and keep a steady, moderate speed through both bends.",
        "parking_impact": "❌ NO PARKING along S-bend roads.",
        "rule_type": "NO_PARKING",
        "penalty": "Fine for hazardous driving."
    },
    "LENGTH_LIMIT": {
        "name": "Vehicle Length Limit (अधिकतम लंबाई सीमा)",
        "category": "Turning Clearance",
        "meaning": "Vehicles longer than the specified length (e.g. 10 meters) cannot navigate the narrow alleys or sharp turns ahead.",
        "wrong_meaning": "Thinking: 'Long multi-axle trailers can manage if the driver is skilled.' — WRONG! The street corners are physically too tight and long trucks get permanently stuck.",
        "driver_action": "Long buses and trailers must turn back and take commercial ring roads.",
        "parking_impact": "❌ Long vehicles cannot park on narrow streets.",
        "rule_type": "NO_PARKING",
        "penalty": "₹2,000 fine + crane removal costs."
    },
    "LOAD_LIMIT": {
        "name": "Maximum Gross Weight Limit (अधिकतम भार सीमा)",
        "category": "Bridge / Road Capacity",
        "meaning": "Total vehicle weight including cargo (e.g., 5 tonnes) cannot exceed this limit. Weak road or culvert ahead.",
        "wrong_meaning": "Thinking: 'It's just an estimate; an extra 2-3 tonnes won't hurt.' — WRONG! Bridges collapse under unrated overloaded weights.",
        "driver_action": "Empty or reroute trucks that exceed the weight limit.",
        "parking_impact": "❌ Heavy vehicles cannot park on load-restricted bridges.",
        "rule_type": "NO_PARKING",
        "penalty": "Overloading fine under Motor Vehicles Act (₹20,000+)."
    },
    "LOOSE_GRAVEL": {
        "name": "Loose Gravel / Road Metal (सड़क पर गिट्टी / कंकड़)",
        "category": "Skid Hazard",
        "meaning": "Loose stone chips, gravel, or unpaved road construction ahead. Tires easily slip and fling flying stones.",
        "wrong_meaning": "Thinking: 'I should brake hard if my car slips.' — WRONG! Hard braking on loose gravel locks wheels and causes instant skidding and rollover.",
        "driver_action": "Slow down smoothly, avoid sudden steering jerks, and leave extra distance behind other cars to avoid windshield stone cracks.",
        "parking_impact": "⚠️ Park carefully on soft road gravel shoulders.",
        "rule_type": "ALLOWED",
        "penalty": "Safety risk."
    },
    "PASS_EITHER_SIDE": {
        "name": "Pass on Either Side (दोनों तरफ से निकल सकते हैं)",
        "category": "Traffic Island Split",
        "meaning": "Traffic splits around a center island or pillar ahead. You can legally drive around either the left or right side.",
        "wrong_meaning": "Thinking: 'The right branch enters oncoming traffic.' — WRONG! Both sides lead in your direction around the traffic island.",
        "driver_action": "Choose the clearer lane ahead and proceed smoothly without stopping.",
        "parking_impact": "❌ STRICT NO PARKING at the nose of traffic splitter islands.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 fine for lane obstruction."
    },
    "PRIORITY_FOR_ONCOMING_VEHICLES": {
        "name": "Give Priority to Oncoming Cars (सामने वाली गाड़ी को पहले जाने दें)",
        "category": "Narrow Road Priority",
        "meaning": "Narrow passage or single-lane bridge ahead. Cars coming from the opposite direction have legal right of way; you must wait.",
        "wrong_meaning": "Thinking: 'Whoever enters the bridge first gets to cross.' — WRONG! Red arrow indicates YOU must yield and wait for oncoming cars to cross first.",
        "driver_action": "Stop before the narrow bottleneck, flash headlights politely, and let opposite cars cross completely.",
        "parking_impact": "❌ ZERO STOPPING OR PARKING near single-lane bottlenecks.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for blocking a single-lane bridge."
    },
    "QUAY_SIDE_OR_RIVER_BANK": {
        "name": "Riverbank / Canal Edge Ahead (नदी या नहर का किनारा)",
        "category": "Water Hazard",
        "meaning": "Unprotected riverbank, lake promenade, or canal edge ahead without strong safety guardrails.",
        "wrong_meaning": "Thinking: 'The embankment has a barrier that will catch my car.' — WRONG! Many canal banks have no barrier; inattentive driving plunges cars into deep water.",
        "driver_action": "Drive slowly, keep headlights on at night, and stay well away from water edges.",
        "parking_impact": "❌ Do not park close to steep unbarricaded river edges. Apply handbrake and gear firmly if parking.",
        "rule_type": "ALLOWED",
        "penalty": "Severe water hazard."
    },
    "RIGHT_HAIR_PIN_BEND": {
        "name": "Hairpin Bend to the Right (दायाँ हेयरपिन मोड़)",
        "category": "Mountain Blind Turn",
        "meaning": "Extreme 180-degree steep curve turning to the right ahead in hilly terrain.",
        "wrong_meaning": "Thinking: 'I can cut across the right corner to make turning easier.' — WRONG! Cutting across blind right hairpins leads to head-on crashes with downhill trucks.",
        "driver_action": "Stay strictly in your lane, sound your horn, use low gear, and take the turn wide and slow.",
        "parking_impact": "❌ NO PARKING within 50 meters of mountain hairpin bends.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,500 fine for hazardous mountain parking."
    },
    "RIGHT_HAND_CURVE": {
        "name": "Gentle Right Curve Ahead (दायाँ मोड़ आगे है)",
        "category": "Road Alignment",
        "meaning": "Road sweeps to the right. Visibility of oncoming vehicles is reduced.",
        "wrong_meaning": "Thinking: 'I can overtake around the curve if I honk.' — WRONG! Never overtake around any curve, even gentle ones.",
        "driver_action": "Slow down slightly and follow your lane markings around the bend.",
        "parking_impact": "❌ Do not park on road curves.",
        "rule_type": "ALLOWED",
        "penalty": "Fine for obstruction on curves."
    },
    "RIGHT_REVERSE_BEND": {
        "name": "Reverse S-Curve to Right (ज़िगज़ैग दायाँ मोड़)",
        "category": "Double Curve Warning",
        "meaning": "Sharp double bend ahead: road turns right first, then quickly turns left.",
        "wrong_meaning": "Thinking: 'I can speed up between the two turns.' — WRONG! The rapid direction shift upsets vehicle stability and causes spin-outs.",
        "driver_action": "Maintain steady, cautious speed through both curves.",
        "parking_impact": "❌ NO PARKING along double curve stretches.",
        "rule_type": "NO_PARKING",
        "penalty": "Fine for improper parking."
    },
    "ROAD_WIDENS_AHEAD": {
        "name": "Road Widens Ahead (सड़क आगे चौड़ी हो रही है)",
        "category": "Road Expansion",
        "meaning": "The road expands from narrow lanes to multiple wide lanes ahead (e.g. 2 lanes to 4 lanes).",
        "wrong_meaning": "Thinking: 'I can immediately veer right without checking mirrors.' — WRONG! Fast cars from behind will accelerate into newly opened lanes.",
        "driver_action": "Check your rearview mirrors, signal before moving into new lanes, and merge smoothly.",
        "parking_impact": "Park only in marked parking bays, not on active running lanes.",
        "rule_type": "ALLOWED",
        "penalty": "Standard parking rules."
    },
    "SIDE_ROAD_LEFT": {
        "name": "Side Road to Left (बायाँ साइड रोड)",
        "category": "Intersection Warning",
        "meaning": "A smaller side road joins your street from the left side. Vehicles may turn into your path.",
        "wrong_meaning": "Thinking: 'Side road cars will always see my headlights and stop.' — WRONG! Many drivers pop out without looking. Watch left corners closely.",
        "driver_action": "Keep your foot hovering over the brake pedal when passing side street openings.",
        "parking_impact": "❌ NO PARKING within 10 meters of a side street mouth.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 fine for corner parking."
    },
    "SIDE_ROAD_RIGHT": {
        "name": "Side Road to Right (दायाँ साइड रोड)",
        "category": "Intersection Warning",
        "meaning": "A side street joins from the right side ahead.",
        "wrong_meaning": "Thinking: 'I can overtake past the right side junction.' — WRONG! Overtaking past right junctions leads to crashes with cars turning into the side street.",
        "driver_action": "Watch for turning cars and keep intersections clear.",
        "parking_impact": "❌ NO PARKING blocking the side street mouth.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 fine."
    },
    "STAGGERED_INTERSECTION": {
        "name": "Staggered Junction (आगे-पीछे दो मोड़)",
        "category": "Offset Intersection",
        "meaning": "Two closely spaced side roads join from opposite sides: one slightly ahead of the other (zigzag crossing).",
        "wrong_meaning": "Thinking: 'It's a normal straight crossroads.' — WRONG! Crossing traffic zigzags across your lane between the two offset side roads.",
        "driver_action": "Slow down and watch for vehicles crossing between the left and right openings.",
        "parking_impact": "❌ NO PARKING anywhere between the two staggered junction mouths.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for junction obstruction."
    },
    "STEEP_ASCENT": {
        "name": "Steep Uphill Climb Ahead (सीधी चढ़ाई आगे है)",
        "category": "Gradient Warning",
        "meaning": "Road climbs steeply uphill. Heavy trucks ahead will slow down dramatically to 10-20 km/h.",
        "wrong_meaning": "Thinking: 'I should follow closely behind heavy trucks uphill.' — WRONG! Heavily loaded trucks frequently stall or roll backward on steep climbs.",
        "driver_action": "Shift to a lower gear before starting the climb and leave 3 to 4 car lengths behind trucks.",
        "parking_impact": "⚠️ If parking on an incline, turn your wheels toward the curb and pull handbrake firmly.",
        "rule_type": "ALLOWED",
        "penalty": "Safety risk of rollback."
    },
    "STEEP_DESCENT": {
        "name": "Steep Downhill Slope Ahead (खतरनाक ढलान आगे है)",
        "category": "Gradient Warning",
        "meaning": "Road slopes steeply downhill. Your car will accelerate naturally due to gravity.",
        "wrong_meaning": "Thinking: 'Putting the car in neutral (freewheeling) saves fuel downhill.' — WRONG! Extremely dangerous! Brakes overheat and completely fail without engine braking.",
        "driver_action": "Engage lower gear (2nd or 3rd) and let engine braking control vehicle speed. Do not ride the brakes continuously.",
        "parking_impact": "⚠️ Turn wheels toward curb and apply handbrake firmly if parking on downward slopes.",
        "rule_type": "ALLOWED",
        "penalty": "Fine for negligent downhill driving."
    },
    "TONGA_PROHIBITED": {
        "name": "No Horse-Drawn Carts / Tongas (तांगा मना है)",
        "category": "Slow Traffic Restriction",
        "meaning": "Horse-drawn carriages (tongas) are prohibited on this fast urban flyover or highway.",
        "wrong_meaning": "Thinking: 'Tongas are allowed if they stay on the extreme edge.' — WRONG! Animals panic in heavy motor traffic and cause multi-vehicle pileups.",
        "driver_action": "Use designated heritage carriage routes or rural streets.",
        "parking_impact": "❌ No tying animals or parking carriages on roadsides.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 fine under Police Regulations."
    },
    "TURN_RIGHT": {
        "name": "Turn Right (दाएँ मुड़ें)",
        "category": "Mandatory Direction",
        "meaning": "Sharp right turn ahead. Follow the roadway to the right.",
        "wrong_meaning": "Thinking: 'I can cut across the incoming lane to turn quickly.' — WRONG! Cutting corners causes head-on collisions with oncoming vehicles.",
        "driver_action": "Slow down, indicate right, and stay on your side of the white center dividing line.",
        "parking_impact": "❌ NO PARKING along the turn.",
        "rule_type": "NO_PARKING",
        "penalty": "₹500 fine for lane violation."
    },
    "T_INTERSECTION": {
        "name": "T-Junction Ahead (T-पॉइंट आगे है)",
        "category": "Road Dead End Warning",
        "meaning": "The road you are driving on terminates ahead at a perpendicular road (T-junction). You cannot go straight; you must turn left or right.",
        "wrong_meaning": "Thinking: 'The road continues straight through.' — WRONG! Speeding straight ahead will crash your car into the opposite boundary wall or ditch.",
        "driver_action": "Brake early, come to a near stop, look both directions, and turn into the cross street.",
        "parking_impact": "❌ STRICT NO PARKING directly facing the stem of a T-junction.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for parking at a dead-end T-junction."
    },
    "WIDTH_LIMIT": {
        "name": "Maximum Width Limit (अधिकतम चौड़ाई सीमा)",
        "category": "Narrow Passage Limit",
        "meaning": "Vehicles wider than the indicated width (e.g. 2.0 meters) cannot pass. Narrow heritage gates or alleys ahead.",
        "wrong_meaning": "Thinking: 'My wide car will fit if I fold my mirrors.' — WRONG! Concrete bollards will wedge your doors and scrape panels.",
        "driver_action": "Wide SUVs and trucks must turn back and take wide arterial roads.",
        "parking_impact": "❌ Never park on narrow width-restricted streets; it completely blocks ambulances and fire engines.",
        "rule_type": "NO_PARKING",
        "penalty": "₹2,000 fine for blocking emergency access."
    },
    "Y_INTERSECTION": {
        "name": "Y-Junction Ahead (Y-आकार का मोड़)",
        "category": "Fork Ahead",
        "meaning": "The road splits into two distinct angled branches ahead like the letter 'Y'.",
        "wrong_meaning": "Thinking: 'I can brake suddenly at the fork to decide which way to go.' — WRONG! Stopping at highway fork points causes severe rear-end pileups.",
        "driver_action": "Check overhead directional signs early, get into your chosen left or right lane well before the split, and do not make last-second swerves.",
        "parking_impact": "❌ STRICT TOW-AWAY ZONE inside the V-shaped chevron gore area between fork lanes.",
        "rule_type": "NO_PARKING",
        "penalty": "₹1,000 fine for parking in highway gore areas."
    },
}


def get_sign_intelligence(class_name: str) -> dict:
    """
    Returns crystal-clear, easy-to-understand plain language for any sign class.
    Includes 'wrong_meaning' (common misconceptions drivers have).
    """
    if not class_name:
        info = SIGN_KNOWLEDGE["NOT_DETECTED"].copy()
        info["sign_key"] = "NOT_DETECTED"
        return info

    key = class_name.strip().upper()

    if key in ["NOT_DETECTED", "UNKNOWN", "NONE", "NO_SIGN", "EMPTY"]:
        info = SIGN_KNOWLEDGE["NOT_DETECTED"].copy()
        info["sign_key"] = "NOT_DETECTED"
        return info

    if key in SIGN_KNOWLEDGE:
        info = SIGN_KNOWLEDGE[key].copy()
        info["sign_key"] = key
        return info

    # Check for U-turn variations
    if "U_TURN" in key or "UTURN" in key:
        if "PROHIBIT" in key or "NO" in key:
            info = SIGN_KNOWLEDGE["U_TURN_PROHIBITED"].copy()
            info["sign_key"] = "U_TURN_PROHIBITED"
            return info
        else:
            info = SIGN_KNOWLEDGE["U_TURN"].copy()
            info["sign_key"] = "U_TURN"
            return info

    if "GAP_IN_MEDIAN" in key:
        info = SIGN_KNOWLEDGE["GAP_IN_MEDIAN"].copy()
        info["sign_key"] = "GAP_IN_MEDIAN"
        return info

    # Format human-friendly name from slug (e.g. "LEFT_HAIR_PIN_BEND" -> "Left Hair Pin Bend")
    friendly_name = key.replace("_", " ").title()
    category = "Traffic Guide Sign"
    rule_type = "ALLOWED"
    penalty = "Traffic fine for disobeying road signs under Motor Vehicles Act."

    # Easy plain language categorization
    if "NO_PARK" in key or "NO_STOP" in key or "TOW" in key:
        category = "No Parking Rule"
        rule_type = "NO_PARKING"
        meaning = f"You are not allowed to park your car or bike here ({friendly_name}). This area must remain clear."
        wrong_meaning = "Thinking: 'I can wait here for a few minutes with my parking hazard blinkers on.' — WRONG! Hazard lights do NOT give permission to park in a No-Parking area."
        action = "Do not park here. If you park, traffic police will tow your vehicle away."
        parking_impact = "❌ NO PARKING. Active tow-away zone."
        penalty = "₹500 to ₹1,000 fine + Towing charges."

    elif "PROHIBIT" in key or "NO_ENTRY" in key or "STOP" in key:
        category = "Strict Prohibition"
        rule_type = "NO_PARKING"
        meaning = f"This sign means you are NOT allowed to perform this movement: {friendly_name}."
        wrong_meaning = "Thinking: 'This restriction is only for big vehicles or trucks.' — WRONG! This applies equally to cars, bikes, and all vehicles."
        action = "Follow the restriction carefully and do not enter or block this road."
        parking_impact = "❌ NO PARKING allowed on this restricted roadway."
        penalty = "₹500 to ₹1,000 fine."

    elif "COMPULSARY" in key or "MANDATORY" in key:
        category = "Must Follow Direction"
        rule_type = "ALLOWED"
        meaning = f"You MUST follow this exact direction: {friendly_name}. Turning in any other direction is not allowed."
        wrong_meaning = "Thinking: 'This direction is just a suggestion or recommendation.' — WRONG! Blue circular signs are legally MANDATORY under Indian law."
        action = f"Follow the arrow ({friendly_name}). Do not stop on the corner to block other cars."
        parking_impact = "⚠️ Keep the turn clear. Park only in authorized side bays."
        penalty = "₹500 fine for blocking the lane."

    elif "SPEED_LIMIT" in key:
        speed = "".join(filter(str.isdigit, key)) or "indicated"
        category = "Speed Limit"
        rule_type = "ALLOWED"
        meaning = f"Do not drive faster than {speed} km/h on this road. Keep your speedometer at or below {speed}."
        wrong_meaning = f"Thinking: 'I can drive 10 km/h above {speed} km/h without getting a challan.' — WRONG! Speed cameras detect and fine even 1 km/h above the limit."
        action = f"Maintain speed under {speed} km/h."
        parking_impact = "Park only in marked parking spaces on the side."
        penalty = f"₹1,000 to ₹2,000 online challan for driving over {speed} km/h."

    elif "BEND" in key or "CURVE" in key or "HAIR_PIN" in key:
        category = "Sharp Turn Warning"
        rule_type = "NO_PARKING"
        meaning = f"Sharp curve ahead ({friendly_name})! You cannot see oncoming cars around this corner."
        wrong_meaning = "Thinking: 'I can overtake on this turn if I accelerate quickly.' — WRONG! Overtaking on blind curves causes fatal head-on crashes."
        action = "Slow down, stay in your lane, and blow your horn before turning."
        parking_impact = "❌ NEVER PARK ON A CURVE OR TURN. Other cars might crash into you."
        penalty = "Fine for dangerous parking on curves."

    elif "INTERSECTION" in key or "CROSS" in key or "ROAD" in key or "SIDE" in key:
        category = "Junction Ahead"
        rule_type = "NO_PARKING"
        meaning = f"Road junction ahead ({friendly_name}) where other vehicles will join or cross your lane."
        wrong_meaning = "Thinking: 'I can park near the corner if I leave enough room for cars.' — WRONG! Parking within 15 meters of any intersection is strictly illegal."
        action = "Slow down, check both sides, and let crossing traffic pass safely."
        parking_impact = "❌ NO PARKING within 15 meters of any intersection."
        penalty = "₹500 fine for blocking an intersection."

    elif "AHEAD" in key or "HAZARD" in key or "DIP" in key or "STEEP" in key:
        category = "Caution Ahead"
        rule_type = "ALLOWED"
        meaning = f"Be alert: {friendly_name} ahead on the road. Drive with extra care."
        wrong_meaning = "Thinking: 'Hazard signs are just advisory, no need to slow down.' — WRONG! Ignoring road hazard signs leads to suspension damage and rollovers."
        action = "Slow down and pay close attention to the road surface."
        parking_impact = "Be cautious when parking on steep or uneven road edges."

    else:
        meaning = f"Official traffic sign for '{friendly_name}'. Follow standard driving discipline."
        wrong_meaning = "Thinking: 'I can ignore this sign if there are no traffic police nearby.' — WRONG! Automated CCTV cameras detect and fine sign violations automatically."
        action = "Observe the sign and follow traffic rules."
        parking_impact = "Standard public parking rules apply."

    return {
        "sign_key": key,
        "name": friendly_name,
        "category": category,
        "meaning": meaning,
        "wrong_meaning": wrong_meaning,
        "driver_action": action,
        "parking_impact": parking_impact,
        "rule_type": rule_type,
        "penalty": penalty
    }
