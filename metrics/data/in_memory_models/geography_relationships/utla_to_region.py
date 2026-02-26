UTLA_TO_REGION_LOOKUP: dict[str, str] = {
    "E06000001": "North East",                      # Hartlepool
    "E06000002": "North East",                      # Middlesborough
    "E06000003": "North East",                      # Redcar and Cleveland
    "E06000004": "North East",                      # Stockton-on-Tees
    "E06000005": "North East",                      # Darlington
    "E06000006": "North West",                      # Halton
    "E06000007": "North West",                      # Warrington
    "E06000008": "North West",                      # Blackburn with Darwen
    "E06000009": "North West",                      # Blackpool
    "E06000010": "Yorkshire and The Humber",        # Kingston upon Hull, City of
    "E06000011": "Yorkshire and The Humber",        # East Riding of Yorkshire
    "E06000012": "Yorkshire and The Humber",        # North East Lincolnshire
    "E06000013": "Yorkshire and The Humber",        # North Lincolnshire
    "E06000014": "Yorkshire and The Humber",        # York
    "E06000015": "East Midlands",                   # Derby
    "E06000016": "East Midlands",                   # Leicester
    "E06000017": "East Midlands",                   # Rutland
    "E06000018": "East Midlands",                   # Nottingham
    "E06000019": "West Midlands",                   # Herefordshire, County of
    "E06000020": "West Midlands",                   # Telford and Wrekin
    "E06000021": "West Midlands",                   # Stoke-on-Trent
    "E06000022": "South West",                      # Bath and North Somerset
    "E06000023": "South West",                      # Bristol, City of
    "E06000024": "South West",                      # North Somerset
    "E06000025": "South West",                      # South Gloucestershire
    "E06000026": "South West",                      # Plymouth
    "E06000027": "South West",                      # Torbay
    "E06000030": "South West",                      # Swindon
    "E06000031": "East of England",                 # Peterborough
    "E06000032": "East of England",                 # Luton
    "E06000033": "East of England",                 # Southend-on-Sea
    "E06000034": "East of England",                 # Thurrock
    "E06000035": "South East",                      # Medway
    "E06000036": "South East",                      # Bracknell Forest
    "E06000037": "South East",                      # West Berkshire
    "E06000038": "South East",                      # Reading
    "E06000039": "South East",                      # Slough
    "E06000040": "South East",                      # Windsor and Maidenhead
    "E06000041": "South East",                      # Wokingham
    "E06000042": "South East",                      # Milton Keynes
    "E06000043": "South East",                      # Brighton and Hove
    "E06000044": "South East",                      # Portsmouth
    "E06000045": "South East",                      # Southampton
    "E06000046": "South East",                      # Isle of Wight
    "E06000047": "North East",                      # County Durham
    "E06000049": "North West",                      # Cheshire East
    "E06000050": "North West",                      # Cheshire West and Chester
    "E06000051": "West Midlands",                   # Shropshire
    "E06000052": "South West",                      # Cornwall
    "E06000053": "South West",                      # Isles of Scilly
    "E06000054": "South West",                      # Wiltshire
    "E06000055": "East of England",                 # Bedford
    "E06000056": "East of England",                 # Central Bedforshire
    "E06000057": "North East",                      # Northumberland
    "E06000058": "South West",                      # Bournemouth, Christchurch and Poole
    "E06000059": "South West",                      # Dorset
    "E06000060": "South East",                      # Buckinghamshire
    "E06000061": "East Midlands",                   # North Northamptonshire
    "E06000062": "East Midlands",                   # West Northamptonshire
    "E06000063": "North West",                      # Cumberland
    "E06000064": "North West",                      # Westmorland and Furness
    "E10000023": "Yorkshire and The Humber",        # North Yorkshire
    "E10000027": "South West",                      # Somerset
    "E08000001": "North West",                      # Bolton
    "E08000002": "North West",                      # Bury
    "E08000003": "North West",                      # Manchester
    "E08000004": "North West",                      # Oldham
    "E08000005": "North West",                      # Rochdale
    "E08000006": "North West",                      # Salford
    "E08000007": "North West",                      # Stockport
    "E08000008": "North West",                      # Tameside
    "E08000009": "North West",                      # Trafford
    "E08000010": "North West",                      # Wigan
    "E08000011": "North West",                      # Knowsley
    "E08000012": "North West",                      # Liverpool
    "E08000013": "North West",                      # St. Helens
    "E08000014": "North West",                      # Sefton
    "E08000015": "North West",                      # Wirral
    "E08000016": "Yorkshire and The Humber",        # Barnsley
    "E08000017": "Yorkshire and The Humber",        # Doncaster
    "E08000018": "Yorkshire and The Humber",        # Rotherham
    "E08000019": "Yorkshire and The Humber",        # Sheffield
    "E08000021": "North East",                      # Newcastle upon Tyne
    "E08000022": "North East",                      # North Tyneside
    "E08000023": "North East",                      # South Tyneside
    "E08000024": "North East",                      # Sunderland
    "E08000025": "West Midlands",                   # Birmingham
    "E08000026": "West Midlands",                   # Coventry
    "E08000027": "West Midlands",                   # Dudley
    "E08000028": "West Midlands",                   # Sandwell
    "E08000029": "West Midlands",                   # Solihull
    "E08000030": "West Midlands",                   # Walsall
    "E08000031": "West Midlands",                   # Wolverhampton
    "E08000032": "Yorkshire and The Humber",        # Bradford
    "E08000033": "Yorkshire and The Humber",        # Calderdale
    "E08000034": "Yorkshire and The Humber",        # Kirklees
    "E08000035": "Yorkshire and The Humber",        # Leeds
    "E08000036": "Yorkshire and The Humber",        # Wakefield
    "E08000037": "North East",                      # Gateshead
    "E09000001": "London",                          # City of London
    "E09000002": "London",                          # Barking and Dagenham
    "E09000003": "London",                          # Barnet
    "E09000004": "London",                          # Bexley
    "E09000005": "London",                          # Brent
    "E09000006": "London",                          # Bromley
    "E09000007": "London",                          # Camden
    "E09000008": "London",                          # Croydon
    "E09000009": "London",                          # Ealing
    "E09000010": "London",                          # Enfield
    "E09000011": "London",                          # Greenwich
    "E09000012": "London",                          # Hackney
    "E09000013": "London",                          # Hammersmith and Fulham
    "E09000014": "London",                          # Haringey
    "E09000015": "London",                          # Harrow
    "E09000016": "London",                          # Havering
    "E09000017": "London",                          # Hillingdon
    "E09000018": "London",                          # Hounslow
    "E09000019": "London",                          # Islington
    "E09000020": "London",                          # Kensington and Chelsea
    "E09000021": "London",                          # Kingston upon Thames
    "E09000022": "London",                          # Lambeth
    "E09000023": "London",                          # Lewisham
    "E09000024": "London",                          # Merton
    "E09000025": "London",                          # Newham
    "E09000026": "London",                          # Redbridge
    "E09000027": "London",                          # Richmond upon Thames
    "E09000028": "London",                          # Southwark
    "E09000029": "London",                          # Sutton
    "E09000030": "London",                          # Tower Hamlets
    "E09000031": "London",                          # Waltham Forest
    "E09000032": "London",                          # Wandsworth
    "E09000033": "London",                          # Westminster
    "E10000003": "East of England",                 # Cambridgeshire
    "E10000006": "North West",                      # Cumbria
    "E10000007": "East Midlands",                   # Derbyshire
    "E10000008": "South West",                      # Devon
    "E10000011": "South East",                      # East Sussex
    "E10000012": "East of England",                 # Essex
    "E10000013": "South West",                      # Gloucestershire
    "E10000014": "South East",                      # Hampshire
    "E10000015": "East of England",                 # Hertfordshire
    "E10000016": "South East",                      # Kent
    "E10000017": "North West",                      # Lancashire
    "E10000018": "East Midlands",                   # Leicestershire
    "E10000019": "East Midlands",                   # Lincolnshire
    "E10000020": "East of England",                 # Norfolk
    "E10000024": "East Midlands",                   # Nottinghamshire
    "E10000025": "South East",                      # Oxfordshire
    "E10000028": "West Midlands",                   # Staffordshire
    "E10000029": "East of England",                 # Suffolk
    "E10000030": "South East",                      # Surrey
    "E10000031": "West Midlands",                   # Warwickshire
    "E10000032": "South East",                      # West Sussex
    "E10000034": "West Midlands",                   # Worcestershire
}
