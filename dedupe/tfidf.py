import collections
import math
import re
import core

class TfidfPredicate:
  def __init__(self, threshold) :
    self.threshold = threshold


def coverage(threshold, field, training_pairs, inverted_index) :

  docs = set(instance for pair in training_pairs for instance in pair)

  corpus = dict((i, doc[field]) for i, doc in enumerate(docs))
  id_lookup = dict((instance, i) for i, instance in enumerate(docs))

  blocked_data = createCanopies(corpus, inverted_index, threshold)

  coverage_dict = {}

  for pair in training_pairs:
    id_pair = set(id_lookup[instance] for instance in pair)
    
    if any(id_pair.issubset(block) for block in blocked_data) :
      coverage_dict[pair] = 1
    else:
      coverage_dict[pair] = -1

  return coverage_dict

def documentFrequency(corpus) : 
  num_docs = 0
  term_num_docs = collections.defaultdict(int)
  num_docs = len(corpus)

  for doc_id, doc in corpus.iteritems() :
    tokens = getTokens(doc)
    for token in set(tokens) :
      term_num_docs[token] += 1

  for term, count in term_num_docs.iteritems() :
    term_num_docs[term] = math.log((num_docs + 0.5) / (float(count) + 0.5))

  term_num_docs_default = collections.defaultdict(lambda: math.log((num_docs + 0.5)/0.5))    # term : num_docs_containing_term
  term_num_docs_default.update(term_num_docs)

  return term_num_docs_default

def invertedIndex(corpus):
  inverted_index = collections.defaultdict(list)
  for doc_id, doc in corpus.iteritems() :
    tokens = getTokens(doc)
    for token in set(tokens) :
      inverted_index[token].append(doc_id)

  return inverted_index

def getTokens(str):
  return re.findall(r"[\w'@#]+", str.lower())

def createCanopies(corpus_original, df_index, threshold) :
  blocked_data = []
  seen_set = set([])
  corpus = corpus_original.copy()
  inverted_index = invertedIndex(corpus)
  while corpus :
    doc_id, center = corpus.popitem()
    if not center :
      continue
    
    seen_set.add(doc_id)
    block = [doc_id]
    candidate_set = set([])
    tokens = getTokens(center)
    center_dict = tfidfDict(center, df_index)

    for token in tokens :
      candidate_set.update(inverted_index[token])

    candidate_set = candidate_set - seen_set
    for doc_id in candidate_set :
      candidate_dict = tfidfDict(corpus[doc_id], df_index)
      similarity = cosineSimilarity(candidate_dict, center_dict)

      if similarity > threshold :
        block.append(doc_id)
        seen_set.add(doc_id)
        del corpus[doc_id]

    if len(block) > 1 :
      blocked_data.append(block)

  return blocked_data

def cosineSimilarity(doc_dict_1, doc_dict_2) :
  dot_product = 0

  common_keys = set(doc_dict_1.keys()) & set(doc_dict_2.keys())
  for key in common_keys :
    dot_product += doc_dict_1[key] * doc_dict_2[key]

  norm_1 = calculateNorm(doc_dict_1)
  norm_2 = calculateNorm(doc_dict_2)

  return dot_product / (norm_1 * norm_2)

def calculateNorm(doc_dict) :
  norm = 0
  for value in doc_dict.values() :
    norm += value*value

  return math.sqrt(norm) 

def tfidfDict(doc, df_index) :
  tokens = getTokens(doc)
  doc_dict = {}
  for token in set(tokens) :
    doc_dict[token] = tokens.count(token) * df_index[token]

  return doc_dict

# testing basic TF-IDF
# corpus = {1: "Forest is cool and stuff", 2: "Derek is cool and maybe other stuff"}
# a = documentFrequency(corpus)
# print a
# print a['foo']

# testing cosineSimilarity
# doc_1 = {"a": 1, "cat": 1, "sat": 1}
# doc_2 = {"a": 1, "bat": 1, "sat": 1}

# print cosineSimilarity(doc_1, doc_2)

# testing tfidfDict
# corpus = {1: "Forest is cool and stuff", 2: "Derek is cool and maybe other stuff"}
# inverted_index = documentFrequency(corpus)
# print inverted_index
# tf_dict_1 = tfidfDict("Forest is cool", inverted_index)
# print tf_dict_1
# tf_dict_2 = tfidfDict("Forest is not cool", inverted_index)
# print tf_dict_2

# print cosineSimilarity(tf_dict_1, tf_dict_2)

# restaurants = ["arnie morton's of chicago",
# "arnie morton's of chicago",
# "art's delicatessen",
# "art's deli",
# "hotel bel-air",
# "bel-air hotel",
# "cafe bizou",
# "cafe bizou",
# "campanile",
# "campanile",
# "chinois on main",
# "chinois on main",
# "citrus",
# "citrus",
# "fenix",
# "fenix at the argyle",
# "granita",
# "granita",
# "grill on the alley",
# "grill  the",
# "restaurant katsu",
# "katsu",
# "l'orangerie",
# "l'orangerie",
# "le chardonnay",
# "le chardonnay (los angeles)",
# "locanda veneta",
# "locanda veneta",
# "matsuhisa",
# "matsuhisa",
# "the palm",
# "palm  the (los angeles)",
# "patina",
# "patina",
# "philippe's the original",
# "philippe the original",
# "pinot bistro",
# "pinot bistro",
# "rex il ristorante",
# "rex il ristorante",
# "spago",
# "spago (los angeles)",
# "valentino",
# "valentino",
# "yujean kang's gourmet chinese cuisine",
# "yujean kang's",
# "21 club",
# "21 club",
# "aquavit",
# "aquavit",
# "aureole",
# "aureole",
# "cafe lalo",
# "cafe lalo",
# "cafe des artistes",
# "cafe des artistes",
# "carmine's",
# "carmine's",
# "carnegie deli",
# "carnegie deli",
# "chanterelle",
# "chanterelle",
# "daniel",
# "daniel",
# "dawat",
# "dawat",
# "felidia",
# "felidia",
# "four seasons grill room",
# "four seasons",
# "gotham bar & grill",
# "gotham bar & grill",
# "gramercy tavern",
# "gramercy tavern",
# "island spice",
# "island spice",
# "jo jo",
# "jo jo",
# "la caravelle",
# "la caravelle",
# "la cote basque",
# "la cote basque",
# "le bernardin",
# "le bernardin",
# "les celebrites",
# "les celebrites",
# "lespinasse",
# "lespinasse (new york city)",
# "lutece",
# "lutece",
# "manhattan ocean club",
# "manhattan ocean club",
# "march",
# "march",
# "mesa grill",
# "mesa grill",
# "mi cocina",
# "mi cocina",
# "montrachet",
# "montrachet",
# "oceana",
# "oceana",
# "park avenue cafe",
# "park avenue cafe (new york city)",
# "petrossian",
# "petrossian",
# "picholine",
# "picholine",
# "pisces",
# "pisces",
# "rainbow room",
# "rainbow room",
# "river cafe",
# "river cafe",
# "san domenico",
# "san domenico",
# "second avenue deli",
# "second avenue deli",
# "seryna",
# "seryna",
# "shun lee west",
# "shun lee palace",
# "sign of the dove",
# "sign of the dove",
# "smith & wollensky",
# "smith & wollensky",
# "tavern on the green",
# "tavern on the green",
# "uncle nick's",
# "uncle nick's",
# "union square cafe",
# "union square cafe",
# "virgil's",
# "virgil's real bbq",
# "chin's",
# "chin's",
# "coyote cafe",
# "coyote cafe (las vegas)",
# "le montrachet",
# "le montrachet bistro",
# "palace court",
# "palace court",
# "second street grille",
# "second street grill",
# "steak house",
# "steak house  the",
# "tillerman",
# "tillerman  the",
# "abruzzi",
# "abruzzi",
# "bacchanalia",
# "bacchanalia",
# "bone's",
# "bone's restaurant",
# "brasserie le coze",
# "brasserie le coze",
# "buckhead diner",
# "buckhead diner",
# "ciboulette",
# "ciboulette restaurant",
# "delectables",
# "delectables",
# "georgia grille",
# "georgia grille",
# "hedgerose heights inn",
# "hedgerose heights inn  the",
# "heera of india",
# "heera of india",
# "indigo coastal grill",
# "indigo coastal grill",
# "la grotta",
# "la grotta",
# "mary mac's tea room",
# "mary mac's tea room",
# "nikolai's roof",
# "nikolai's roof",
# "pano's and paul's",
# "pano's & paul's",
# "cafe  ritz-carlton  buckhead",
# "ritz-carlton cafe (buckhead)",
# "dining room  ritz-carlton  buckhead",
# "ritz-carlton dining room (buckhead)",
# "restaurant  ritz-carlton  atlanta",
# "ritz-carlton restaurant",
# "toulouse",
# "toulouse",
# "veni vidi vici",
# "veni vidi vici",
# "alain rondelli",
# "alain rondelli",
# "aqua",
# "aqua",
# "boulevard",
# "boulevard",
# "cafe claude",
# "cafe claude",
# "campton place",
# "campton place",
# "chez michel",
# "chez michel",
# "fleur de lys",
# "fleur de lys",
# "fringale",
# "fringale",
# "hawthorne lane",
# "hawthorne lane",
# "khan toke thai house",
# "khan toke thai house",
# "la folie",
# "la folie",
# "lulu",
# "lulu restaurant-bis-cafe",
# "masa's",
# "masa's",
# "mifune japan center  kintetsu building",
# "mifune",
# "plumpjack cafe",
# "plumpjack cafe",
# "postrio",
# "postrio",
# "ritz-carlton restaurant and dining room",
# "ritz-carlton dining room (san francisco)",
# "rose pistola",
# "rose pistola",
# "adriano's ristorante",
# "barney greengrass",
# "beaurivage",
# "bistro garden",
# "border grill",
# "broadway deli",
# "ca'brea",
# "ca'del sol",
# "cafe pinot",
# "california pizza kitchen",
# "canter's",
# "cava",
# "cha cha cha",
# "chan dara",
# "clearwater cafe",
# "dining room",
# "dive!",
# "drago",
# "drai's",
# "dynasty room",
# "eclipse",
# "ed debevic's",
# "el cholo",
# "gilliland's",
# "gladstone's",
# "hard rock cafe",
# "harry's bar & american grill",
# "il fornaio cucina italiana",
# "jack sprat's grill",
# "jackson's farm",
# "jimmy's",
# "joss",
# "le colonial",
# "le dome",
# "louise's trattoria",
# "mon kee seafood restaurant",
# "morton's",
# "nate 'n' al's",
# "nicola",
# "ocean avenue",
# "orleans",
# "pacific dining car",
# "paty's",
# "pinot hollywood",
# "posto",
# "prego",
# "rj's the rib joint",
# "remi",
# "restaurant horikawa",
# "roscoe's house of chicken 'n' waffles",
# "schatzi on main",
# "sofi",
# "swingers",
# "tavola calda",
# "the mandarin",
# "tommy tang's",
# "tra di noi",
# "trader vic's",
# "vida",
# "west beach cafe",
# "20 mott",
# "9 jones street",
# "adrienne",
# "agrotikon",
# "aja",
# "alamo",
# "alley's end",
# "ambassador grill",
# "american place",
# "anche vivolo",
# "arizona",
# "arturo's",
# "au mandarin",
# "bar anise",
# "barbetta",
# "ben benson's",
# "big cup",
# "billy's",
# "boca chica",
# "bolo",
# "boonthai",
# "bouterin",
# "brothers bar-b-q",
# "bruno",
# "bryant park grill  roof restaurant and bp cafe",
# "c3",
# "ct",
# "cafe bianco",
# "cafe botanica",
# "cafe la fortuna",
# "cafe luxembourg",
# "cafe pierre",
# "cafe centro",
# "cafe fes",
# "caffe dante",
# "caffe dell'artista",
# "caffe lure",
# "caffe reggio",
# "caffe roma",
# "caffe vivaldi",
# "caffe bondi ristorante",
# "capsouto freres",
# "captain's table",
# "casa la femme",
# "cendrillon asian grill & marimba bar",
# "chez jacqueline",
# "chiam",
# "china grill",
# "cite",
# "coco pazzo",
# "columbus bakery",
# "corrado cafe",
# "cupcake cafe",
# "da nico",
# "dean & deluca",
# "diva",
# "dix et sept",
# "docks",
# "duane park cafe",
# "el teddy's",
# "emily's",
# "empire korea",
# "ernie's",
# "evergreen cafe",
# "f. ille ponte ristorante",
# "felix",
# "ferrier",
# "fifty seven fifty seven",
# "film center cafe",
# "fiorello's roman cafe",
# "firehouse",
# "first",
# "fishin eddie",
# "fleur de jour",
# "flowers",
# "follonico",
# "fraunces tavern",
# "french roast",
# "french roast cafe",
# "frico bar",
# "fujiyama mama",
# "gabriela's",
# "gallagher's",
# "gianni's",
# "girafe",
# "global",
# "golden unicorn",
# "grand ticino",
# "halcyon",
# "hard rock cafe",
# "hi-life restaurant and lounge",
# "home",
# "hudson river club",
# "i trulli",
# "il cortile",
# "il nido",
# "inca grill",
# "indochine",
# "internet cafe",
# "ipanema",
# "jean lafitte",
# "jewel of india",
# "jimmy sung's",
# "joe allen",
# "judson grill",
# "l'absinthe",
# "l'auberge",
# "l'auberge du midi",
# "l'udo",
# "la reserve",
# "lanza restaurant",
# "lattanzi ristorante",
# "layla",
# "le chantilly",
# "le colonial",
# "le gamin",
# "le jardin",
# "le madri",
# "le marais",
# "le perigord",
# "le select",
# "les halles",
# "lincoln tavern",
# "lola",
# "lucky strike",
# "mad fish",
# "main street",
# "mangia e bevi",
# "manhattan cafe",
# "manila garden",
# "marichu",
# "marquet patisserie",
# "match",
# "matthew's",
# "mavalli palace",
# "milan cafe and coffee bar",
# "monkey bar",
# "montien",
# "morton's",
# "motown cafe",
# "new york kom tang soot bul house",
# "new york noodletown",
# "newsbar",
# "odeon",
# "orso",
# "osteria al droge",
# "otabe",
# "pacifica",
# "palio",
# "pamir",
# "parioli romanissimo",
# "patria",
# "peacock alley",
# "pen & pencil",
# "penang soho",
# "persepolis",
# "planet hollywood",
# "pomaire",
# "popover cafe",
# "post house",
# "rain",
# "red tulip",
# "remi",
# "republic",
# "roettelle a. g",
# "rosa mexicano",
# "ruth's chris",
# "s.p.q.r",
# "sal anthony's",
# "sammy's roumanian steak house",
# "san pietro",
# "sant ambroeus",
# "sarabeth's kitchen",
# "sea grill",
# "serendipity",
# "seventh regiment mess and bar",
# "sfuzzi",
# "shaan",
# "sofia fabulous pizza",
# "spring street natural restaurant & bar",
# "stage deli",
# "stingray",
# "sweet'n'tart cafe",
# "t salon",
# "tang pavillion",
# "tapika",
# "teresa's",
# "terrace",
# "the coffee pot",
# "the savannah club",
# "trattoria dell'arte",
# "triangolo",
# "tribeca grill",
# "trois jean",
# "tse yang",
# "turkish kitchen",
# "two two two",
# "veniero's pasticceria",
# "verbena",
# "victor's cafe",
# "vince & eddie's",
# "vong",
# "water club",
# "west",
# "xunta",
# "zen palate",
# "zoe",
# "abbey",
# "aleck's barbecue heaven",
# "annie's thai castle",
# "anthonys",
# "atlanta fish market",
# "beesley's of buckhead",
# "bertolini's",
# "bistango",
# "cafe renaissance",
# "camille's",
# "cassis",
# "city grill",
# "coco loco",
# "colonnade restaurant",
# "dante's down the hatch  buckhead",
# "dante's down the hatch",
# "fat matt's rib shack",
# "french quarter food shop",
# "holt bros. bar-b-q",
# "horseradish grill",
# "hsu's gourmet",
# "imperial fez",
# "kamogawa",
# "la grotta at ravinia dunwoody rd.",
# "little szechuan",
# "lowcountry barbecue",
# "luna si",
# "mambo restaurante cubano",
# "mckinnon's louisiane",
# "mi spia dunwoody rd.",
# "nickiemoto's: a sushi bar",
# "palisades",
# "pleasant peasant",
# "pricci",
# "r.j.'s uptown kitchen & wine bar",
# "rib ranch",
# "sa tsu ki",
# "sato sushi and thai",
# "south city kitchen",
# "south of france",
# "stringer's fish camp and oyster bar",
# "sundown cafe",
# "taste of new orleans",
# "tomtom",
# "antonio's",
# "bally's big kitchen",
# "bamboo garden",
# "battista's hole in the wall",
# "bertolini's",
# "binion's coffee shop",
# "bistro",
# "broiler",
# "bugsy's diner",
# "cafe michelle",
# "cafe roma",
# "capozzoli's",
# "carnival world",
# "center stage plaza hotel",
# "circus circus",
# "empress court",
# "feast",
# "golden nugget hotel",
# "golden steer",
# "lillie langtry's",
# "mandarin court",
# "margarita's mexican cantina",
# "mary's diner",
# "mikado",
# "pamplemousse",
# "ralph's diner",
# "the bacchanal",
# "venetian",
# "viva mercado's",
# "yolie's",
# "2223",
# "acquarello",
# "bardelli's",
# "betelnut",
# "bistro roti",
# "bix",
# "bizou",
# "buca giovanni",
# "cafe adriano",
# "cafe marimba",
# "california culinary academy",
# "capp's corner",
# "carta",
# "chevys",
# "cypress club",
# "des alpes",
# "faz",
# "fog city diner",
# "garden court",
# "gaylord's",
# "grand cafe hotel monaco",
# "greens",
# "harbor village",
# "harris'",
# "harry denton's",
# "hayes street grill",
# "helmand",
# "hong kong flower lounge",
# "hong kong villa",
# "hyde street bistro",
# "il fornaio levi's plaza",
# "izzy's steak & chop house",
# "jack's",
# "kabuto sushi",
# "katia's",
# "kuleto's",
# "kyo-ya. sheraton palace hotel",
# "l'osteria del forno",
# "le central",
# "le soleil",
# "macarthur park",
# "manora",
# "maykadeh",
# "mccormick & kuleto's",
# "millennium",
# "moose's",
# "north india",
# "one market",
# "oritalia",
# "pacific pan pacific hotel",
# "palio d'asti",
# "pane e vino",
# "pastis",
# "perry's",
# "r&g lounge",
# "rubicon",
# "rumpus",
# "sanppo",
# "scala's bistro",
# "south park cafe",
# "splendido embarcadero",
# "stars",
# "stars cafe",
# "stoyanof's cafe",
# "straits cafe",
# "suppenkuche",
# "tadich grill",
# "the heights",
# "thepin",
# "ton kiang",
# "vertigo",
# "vivande porta via",
# "vivande ristorante",
# "world wrapps",
# "wu kong",
# "yank sing",
# "yaya cuisine",
# "yoyo tsumami bistro",
# "zarzuela",
# "zuni cafe & grill",
# "apple pan  the",
# "asahi ramen",
# "baja fresh",
# "belvedere  the",
# "benita's frites",
# "bernard's",
# "bistro 45",
# "brent's deli",
# "brighton coffee shop",
# "bristol farms market cafe",
# "bruno's",
# "cafe '50s",
# "cafe blanc",
# "cassell's",
# "chez melange",
# "diaghilev",
# "don antonio's",
# "duke's",
# "falafel king",
# "feast from the east",
# "gumbo pot  the",
# "hollywood hills coffee shop",
# "indo cafe",
# "jan's family restaurant",
# "jiraffe",
# "jody maroni's sausage kingdom",
# "joe's",
# "john o'groats",
# "johnnie's pastrami",
# "johnny reb's southern smokehouse",
# "johnny rockets (la)",
# "killer shrimp",
# "kokomo cafe",
# "koo koo roo",
# "la cachette",
# "la salsa (la)",
# "la serenata de garibaldi",
# "langer's",
# "local nochol",
# "main course  the",
# "mani's bakery & espresso bar",
# "martha's",
# "maxwell's cafe",
# "michael's (los angeles)",
# "mishima",
# "mo better meatty meat",
# "mulberry st.",
# "ocean park cafe",
# "ocean star",
# "original pantry bakery",
# "parkway grill",
# "pho hoa",
# "pink's famous chili dogs",
# "poquito mas",
# "r-23",
# "rae's",
# "rubin's red hots",
# "ruby's (la)",
# "russell's burgers",
# "ruth's chris steak house (los angeles)",
# "shiro",
# "sushi nozawa",
# "sweet lady jane",
# "taiko",
# "tommy's",
# "uncle bill's pancake house",
# "water grill",
# "zankou chicken",
# "afghan kebab house",
# "arcadia",
# "benny's burritos",
# "cafe con leche",
# "corner bistro",
# "cucina della fontana",
# "cucina di pesce",
# "darbar",
# "ej's luncheonette",
# "edison cafe",
# "elias corner",
# "good enough to eat",
# "gray's papaya",
# "il mulino",
# "jackson diner",
# "joe's shanghai",
# "john's pizzeria",
# "kelley & ping",
# "kiev",
# "kuruma zushi",
# "la caridad",
# "la grenouille",
# "lemongrass grill",
# "lombardi's",
# "marnie's noodle shop",
# "menchanko-tei",
# "mitali east-west",
# "monsoon (ny)",
# "moustache",
# "nobu",
# "one if by land  tibs",
# "oyster bar",
# "palm",
# "palm too",
# "patsy's pizza",
# "peter luger steak house",
# "rose of india",
# "sam's noodle shop",
# "sarabeth's",
# "sparks steak house",
# "stick to your ribs",
# "sushisay",
# "sylvia's",
# "szechuan hunan cottage",
# "szechuan kitchen",
# "teresa's",
# "thai house cafe",
# "thailand restaurant",
# "veselka",
# "westside cottage",
# "windows on the world",
# "wollensky's grill",
# "yama",
# "zarela",
# "andre's french restaurant",
# "buccaneer bay club",
# "buzio's in the rio",
# "emeril's new orleans fish house",
# "fiore rotisserie & grille",
# "hugo's cellar",
# "madame ching's",
# "mayflower cuisinier",
# "michael's (las vegas)",
# "monte carlo",
# "moongate",
# "morton's of chicago (las vegas)",
# "nicky blair's",
# "piero's restaurant",
# "spago (las vegas)",
# "steakhouse  the",
# "stefano's",
# "sterling brunch",
# "tre visi",
# "103 west",
# "alon's at the terrace",
# "baker's cajun cafe",
# "barbecue kitchen",
# "bistro  the",
# "bobby & june's kountry kitchen",
# "bradshaw's restaurant",
# "brookhaven cafe",
# "cafe sunflower",
# "canoe",
# "carey's",
# "carey's corner",
# "chops",
# "chopstix",
# "deacon burton's soulfood restaurant",
# "eats",
# "flying biscuit  the",
# "frijoleros",
# "greenwood's",
# "harold's barbecue",
# "havana sandwich shop",
# "house of chan",
# "indian delights",
# "java jive",
# "johnny rockets (at)",
# "kalo's coffee house",
# "la fonda latina",
# "lettuce souprise you (at)",
# "majestic",
# "morton's of chicago (atlanta)",
# "my thai",
# "nava",
# "nuevo laredo cantina",
# "original pancake house (at)",
# "palm  the (atlanta)",
# "rainbow restaurant",
# "ritz-carlton cafe (atlanta)",
# "riviera",
# "silver skillet  the",
# "soto",
# "thelma's kitchen",
# "tortillas",
# "van gogh's restaurant & bar",
# "veggieland",
# "white house restaurant",
# "zab-e-lee",
# "bill's place",
# "cafe flore",
# "caffe greco",
# "campo santo",
# "cha cha cha's",
# "doidge's",
# "dottie's true blue cafe",
# "dusit thai",
# "ebisu",
# "emerald garden restaurant",
# "eric's chinese restaurant",
# "hamburger mary's",
# "kelly's on trinity",
# "la cumbre",
# "la mediterranee",
# "la taqueria",
# "mario's bohemian cigar store cafe",
# "marnee thai",
# "mel's drive-in",
# "mo's burgers",
# "phnom penh cambodian restaurant",
# "roosevelt tamale parlor",
# "sally's cafe & bakery",
# "san francisco bbq",
# "slanted door",
# "swan oyster depot",
# "thep phanom",
# "ti couz",
# "trio cafe",
# "tu lan",
# "vicolo pizzeria",
# "wa-ha-ka oaxaca mexican grill"]

# rest_dict = {}
# for i, r in enumerate(restaurants) :
#   rest_dict[i] = r

# #print len(rest_dict)
# inverted_index = documentFrequency(rest_dict)

# blocked_data = createCanopies(rest_dict, inverted_index, 0.8)
# for block in blocked_data :
#   for doc_id in block :
#     print rest_dict[doc_id]
#   print " - end of block - "
# # print blocked_data
# print len(blocked_data)

# from itertools import combinations

# rest_dict = {}
# for i, r in enumerate(restaurants) :
#   rest_dict[i] = r

# training_dict = []
# for r in restaurants :
#   training_dict.append(core.frozendict({"name": r}))

# training_pairs = {0: list(combinations(training_dict, 2)), 1: []}

# #print len(rest_dict)
# inverted_index = documentFrequency(rest_dict)

# cov = coverage(0.6, "name", training_pairs, inverted_index)

# print len(cov)
