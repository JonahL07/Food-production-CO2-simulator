import streamlit as st
import pandas as pd

# =========================================
# 1. PAGE SETUP
# =========================================

st.set_page_config(
    page_title="Land Use & Dietary Simulator",
    page_icon="",
    layout="wide"
)

st.title(" Land Use & Dietary Adequacy Simulator")

st.write(
    "Explore how allocating production amounts of different "
    "food production systems affects greenhouse gas emissions "
    "and the potential to meet population dietary requirements."
)

st.warning(
    "Prototype: all production, emissions and dietry factors are "
    "averaged from real agricultural data for the state of NSW. "
)

# =========================================
# 2. MODEL PARAMETERS
# =========================================

# Yield means edible food produced per hectare per year.
# Emissions are kg of CO2-equivalent per kg of food per year.
# Nutrient values are per kilogram of food.

farms = {
    "Beef": {
        "yield_kg": 10,
        "emissions_kg_kg": 10,
        "carbs_g_kg": 0,
        "protein_g_kg": 250,
        "fat_g_kg": 115,
        "calcium_mg_kg": 150,
        "iron_mg_kg": 32.5,
        "sodium_mg_kg": 650,
        "zinc_mg_kg": 50,
        "vitaminC_mg_kg": 10,
        "vitaminB12_ug_kg": 25,
        "vitaminA_ug_kg": 80,
        "vitaminD_ug_kg": 0.5

    },
    "Wheat": {
        "yield_kg": 10,
        "emissions_kg_kg": 0.15,
        "carbs_g_kg": 20,
        "protein_g_kg": 125,
        "fat_g_kg": 20,
        "calcium_mg_kg": 500,
        "iron_mg_kg": 30,
        "sodium_mg_kg": 35,
        "zinc_mg_kg": 30,
        "vitaminC_mg_kg": 0,
        "vitaminB12_ug_kg": 0,
        "vitaminA_ug_kg": 0,
        "vitaminD_ug_kg": 0
    },
    "Farmed Salmon": {
        "yield_kg": 10,
        "emissions_kg_kg": 8.5,
        "carbs_g_kg": 0,
        "protein_g_kg": 215,
        "fat_g_kg": 150,
        "calcium_mg_kg": 80,
        "iron_mg_kg": 3,
        "sodium_mg_kg": 550,
        "zinc_mg_kg": 5,
        "vitaminC_mg_kg": 35,
        "vitaminB12_ug_kg": 40,
        "vitaminA_ug_kg": 580,
        "vitaminD_ug_kg": 70
    },
    "Potato": {
        "yield_kg": 10,
        "emissions_kg_kg": 0.27,
        "carbs_g_kg": 175,
        "protein_g_kg": 20,
        "fat_g_kg": 1,
        "calcium_mg_kg": 100,
        "iron_mg_kg": 10,
        "sodium_mg_kg": 65,
        "zinc_mg_kg": 3,
        "vitaminC_mg_kg": 140,
        "vitaminB12_ug_kg": 0,
        "vitaminA_ug_kg": 10,
        "vitaminD_ug_kg": 0
    },
    "Tomato": {
        "yield_kg": 10,
        "emissions_kg_kg": 0.22,
        "carbs_g_kg": 40,
        "protein_g_kg": 9,
        "fat_g_kg": 2,
        "calcium_mg_kg": 100,
        "iron_mg_kg": 5,
        "sodium_mg_kg": 65,
        "zinc_mg_kg": 2,
        "vitaminC_mg_kg": 160,
        "vitaminB12_ug_kg": 0,
        "vitaminA_ug_kg": 420,
        "vitaminD_ug_kg": 0
    },
    "Lettuce": {
        "yield_kg": 10,
        "emissions_kg_kg": 0.32,
        "carbs_g_kg": 25,
        "protein_g_kg": 14,
        "fat_g_kg": 1.5,
        "calcium_mg_kg": 180,
        "iron_mg_kg": 5,
        "sodium_mg_kg": 100,
        "zinc_mg_kg": 1.5,
        "vitaminC_mg_kg": 40,
        "vitaminB12_ug_kg": 0,
        "vitaminA_ug_kg": 3000,
        "vitaminD_ug_kg": 0
    },
    "Chickpeas": {
        "yield_kg": 10,
        "emissions_kg_kg": 0.207,
        "carbs_g_kg": 630,
        "protein_g_kg": 200,
        "fat_g_kg": 5,
        "calcium_mg_kg": 550,
        "iron_mg_kg": 45,
        "sodium_mg_kg": 240,
        "zinc_mg_kg": 30,
        "vitaminC_mg_kg": 40,
        "vitaminB12_ug_kg": 0,
        "vitaminA_ug_kg": 30,
        "vitaminD_ug_kg": 0
    },
    "Chicken": {
        "yield_kg": 10,
        "emissions_kg_kg": 4,
        "carbs_g_kg": 0,
        "protein_g_kg": 270,
        "fat_g_kg": 85,
        "calcium_mg_kg": 125,
        "iron_mg_kg": 10,
        "sodium_mg_kg": 550,
        "zinc_mg_kg": 18,
        "vitaminC_mg_kg": 10,
        "vitaminB12_ug_kg": 4,
        "vitaminA_ug_kg": 400,
        "vitaminD_ug_kg": 1
    }
}

# =========================================
# 3. SCENARIO INPUTS
# =========================================

st.header("1. Define your scenario")

population = st.number_input(
    "Population to feed",
    min_value=100_000,
    max_value=10_000_000,
    value=1_000_000,
    step=100_000
)

st.header("2. Set food production quantities")

st.caption(
    "Enter the annual quantity of food produced in tonnes "
    "for each production system."
)

defaults = {
    "Beef": 0,
    "Wheat": 0,
    "Farmed Salmon": 0,
    "Potato": 0,
    "Tomato": 0,
    "Lettuce": 0,
    "Chickpeas": 0,
    "Chicken": 0
}

food_production = {}

for name in farms:
    food_production[name] = st.slider(
        f"{name} production (t/year)",
        min_value=0,
        max_value=1_000_000,
        value=0,
        step=10000,
        key=f"food_{name}"
    )

# =========================================
# 4. CALCULATION ENGINE
# =========================================

results = []

for name, data in farms.items():

    # Food quantity entered directly by the user
    food_tonnes = food_production[name]
    food_kg = food_tonnes * 1000

    # Calculate land required to produce this quantity
    area_ha = (
        food_kg / data["yield_kg"]
        if data["yield_kg"] > 0
        else 0
    )

    # Annual greenhouse gas emissions
    # Assumes emissions_kg_kg means kg CO2e per kg of food
    emissions_kg = food_kg * data["emissions_kg_kg"]

    # Annual nutrient production
    carbohydrates_g = food_kg * data["carbs_g_kg"]
    protein_g = food_kg * data["protein_g_kg"]
    fat_g = food_kg * data["fat_g_kg"]

    calcium_mg = food_kg * data["calcium_mg_kg"]
    iron_mg = food_kg * data["iron_mg_kg"]
    sodium_mg = food_kg * data["sodium_mg_kg"]
    zinc_mg = food_kg * data["zinc_mg_kg"]

    vitaminC_mg = food_kg * data["vitaminC_mg_kg"]
    vitaminB12_ug = food_kg * data["vitaminB12_ug_kg"]
    vitaminA_ug = food_kg * data["vitaminA_ug_kg"]
    vitaminD_ug = food_kg * data["vitaminD_ug_kg"]

    results.append({
        "Production": name,
        "Food (kg/year)": food_kg,
        "Area (ha)": area_ha,
        "Food (tonnes/year)": food_kg / 1000,
        "Emissions (tCO2e/year)": emissions_kg / 1000,
        "Carbohydrates (kg/year)": carbohydrates_g / 1000,
        "Protein (kg/year)": protein_g / 1000,
        "Fat (kg/year)": fat_g / 1000,
        "Calcium (mg/year)": calcium_mg,
        "Iron (mg/year)": iron_mg,
        "Sodium (mg/year)": sodium_mg,
        "Zinc (mg/year)": zinc_mg,
        "Vitamin C (mg/year)": vitaminC_mg,
        "Vitamin B12 (ug/year)": vitaminB12_ug,
        "Vitamin A (ug/year)": vitaminA_ug,
        "Vitamin D (ug/year)": vitaminD_ug
    })

df = pd.DataFrame(results)

# Total production and emissions
total_food = df["Food (tonnes/year)"].sum()
total_emissions = df["Emissions (tCO2e/year)"].sum()

total_carbohydrates_kg = df["Carbohydrates (kg/year)"].sum()
total_protein_kg = df["Protein (kg/year)"].sum()
total_fat_kg = df["Fat (kg/year)"].sum()

total_calcium_mg = df["Calcium (mg/year)"].sum()
total_iron_mg = df["Iron (mg/year)"].sum()
total_sodium_mg = df["Sodium (mg/year)"].sum()
total_zinc_mg = df["Zinc (mg/year)"].sum()

total_vitaminC_mg = df["Vitamin C (mg/year)"].sum()
total_vitaminB12_ug = df["Vitamin B12 (ug/year)"].sum()
total_vitaminA_ug = df["Vitamin A (ug/year)"].sum()
total_vitaminD_ug = df["Vitamin D (ug/year)"].sum()

# Annual population requirements
daily_carbohydrates_per_child = 130
daily_carbohydrates_per_man = 275
daily_carbohydrates_per_woman = 275
daily_carbohydrates_per_older = 130
daily_protein_g_per_child = 30
daily_protein_g_per_man = 60
daily_protein_g_per_woman = 50
daily_protein_g_per_older = 80
daily_fat_g_per_child = 65
daily_fat_g_per_man = 60
daily_fat_g_per_woman = 60
daily_fat_g_per_older = 55
daily_calcium_mg_per_child = 800
daily_calcium_mg_per_man = 840
daily_calcium_mg_per_woman = 970
daily_calcium_mg_per_older = 1100
daily_iron_mg_per_child = 6
daily_iron_mg_per_man = 6
daily_iron_mg_per_woman = 13
daily_iron_mg_per_older = 6
daily_sodium_mg_per_child = 600
daily_sodium_mg_per_man = 1500
daily_sodium_mg_per_woman = 1500
daily_sodium_mg_per_older = 1500
daily_zinc_mg_per_child = 6.5
daily_zinc_mg_per_man = 12
daily_zinc_mg_per_woman = 7.25
daily_zinc_mg_per_older = 9.5
daily_vitaminC_mg_per_child = 35
daily_vitaminC_mg_per_man = 30
daily_vitaminC_mg_per_woman = 30
daily_vitaminC_mg_per_older = 30
daily_vitaminB12_ug_per_child = 1.5
daily_vitaminB12_ug_per_man = 2
daily_vitaminB12_ug_per_woman = 2
daily_vitaminB12_ug_per_older = 2
daily_vitaminA_ug_per_child = 500
daily_vitaminA_ug_per_man = 900
daily_vitaminA_ug_per_woman = 700
daily_vitaminA_ug_per_older = 800
daily_vitaminD_ug_per_child = 15
daily_vitaminD_ug_per_man = 15
daily_vitaminD_ug_per_woman = 15
daily_vitaminD_ug_per_older = 17.5


required_carbohydrates_kg_c = (
    population * 0.18 * daily_carbohydrates_per_child * 365 / 1000
)

required_carbohydrates_kg_m = (
    population * 0.233 * daily_carbohydrates_per_man * 365 / 1000
)

required_carbohydrates_kg_w = (
    population * 0.237 * daily_carbohydrates_per_woman * 365 / 1000
)

required_carbohydrates_kg_o = (
    population * 0.35 * daily_carbohydrates_per_older * 365 / 1000
)

required_protein_kg_c = (
    population * 0.18 * daily_protein_g_per_child * 365 / 1000
)

required_protein_kg_m = (
    population * 0.233 * daily_protein_g_per_man * 365 / 1000
)

required_protein_kg_w = (
    population * 0.237 * daily_protein_g_per_woman * 365 / 1000
)

required_protein_kg_o = (
    population * 0.35 * daily_protein_g_per_older * 365 / 1000
)

required_fat_kg_c = (
    population * 0.18 * daily_fat_g_per_child * 365 / 1000
)

required_fat_kg_m = (
    population * 0.233 * daily_fat_g_per_man * 365 / 1000
)

required_fat_kg_w = (
    population * 0.237 * daily_fat_g_per_woman * 365 / 1000
)

required_fat_kg_o = (
    population * 0.35 * daily_fat_g_per_older * 365 / 1000
)

required_calcium_mg_c = (
    population * 0.18 * daily_calcium_mg_per_child * 365
)

required_calcium_mg_m = (
        population * 0.233 * daily_calcium_mg_per_man * 365
)

required_calcium_mg_w = (
    population * 0.237 * daily_calcium_mg_per_woman * 365
)

required_calcium_mg_o = (
    population * 0.35 * daily_calcium_mg_per_older * 365
)

required_iron_mg_c = (
    population * 0.18 * daily_iron_mg_per_child * 365
)

required_iron_mg_m = (
    population * 0.233 * daily_iron_mg_per_man * 365
)

required_iron_mg_w = (
    population * 0.237 * daily_iron_mg_per_woman * 365
)

required_iron_mg_o = (
    population * 0.35 * daily_iron_mg_per_older * 365
)

required_sodium_mg_c = (
    population * 0.18 * daily_sodium_mg_per_child * 365
)

required_sodium_mg_m = (
    population * 0.233 * daily_sodium_mg_per_man * 365
)

required_sodium_mg_w = (
    population * 0.237 * daily_sodium_mg_per_woman * 365
)

required_sodium_mg_o = (
    population * 0.35 * daily_sodium_mg_per_older * 365
)

required_zinc_mg_c = (
    population * 0.18 * daily_zinc_mg_per_child * 365
)

required_zinc_mg_m = (
    population * 0.233 * daily_zinc_mg_per_man * 365
)

required_zinc_mg_w = (
    population * 0.237 * daily_zinc_mg_per_woman * 365
)

required_zinc_mg_o = (
    population * 0.35 * daily_zinc_mg_per_older * 365
)

required_vitaminC_mg_c = (
    population * 0.18 * daily_vitaminC_mg_per_child * 365
)

required_vitaminC_mg_m = (
    population * 0.233 * daily_vitaminC_mg_per_man * 365
)

required_vitaminC_mg_w = (
    population * 0.237 * daily_vitaminC_mg_per_woman * 365
)

required_vitaminC_mg_o = (
    population * 0.35 * daily_vitaminC_mg_per_older * 365
)

required_vitaminB12_ug_c = (
    population * 0.18 * daily_vitaminB12_ug_per_child * 365
)

required_vitaminB12_ug_m = (
    population * 0.233 * daily_vitaminB12_ug_per_man * 365
)

required_vitaminB12_ug_w = (
    population * 0.237 * daily_vitaminB12_ug_per_woman * 365 
)

required_vitaminB12_ug_o = (
    population * 0.35 * daily_vitaminB12_ug_per_older * 365
)

required_vitaminA_ug_c = (
    population * 0.18 * daily_vitaminA_ug_per_child * 365 
)

required_vitaminA_ug_m = (
    population * 0.233 * daily_vitaminA_ug_per_man * 365 
)

required_vitaminA_ug_w = (
    population * 0.237 * daily_vitaminA_ug_per_woman * 365 
)

required_vitaminA_ug_o = (
    population * 0.35 * daily_vitaminA_ug_per_older * 365 
)

required_vitaminD_ug_c = (
    population * 0.18 * daily_vitaminD_ug_per_child * 365 
)

required_vitaminD_ug_m = (
    population * 0.233 * daily_vitaminD_ug_per_man * 365 
)

required_vitaminD_ug_w = (
    population * 0.237 * daily_vitaminD_ug_per_woman * 365 
)

required_vitaminD_ug_o = (
    population * 0.35 * daily_vitaminD_ug_per_older * 365 
)

# Cap each nutrient score at 100%
carbohydrates_score = min(
    100,
    total_carbohydrates_kg / (required_carbohydrates_kg_c + required_carbohydrates_kg_m +required_carbohydrates_kg_w + required_carbohydrates_kg_o) * 100
)

protein_score = min(
    100,
    total_protein_kg / (required_protein_kg_c + required_protein_kg_m + required_protein_kg_w + required_protein_kg_o) * 100
)

fat_score = min(
    100,
    total_fat_kg / (required_fat_kg_c + required_fat_kg_m + required_fat_kg_w + required_fat_kg_o) * 100
)

calcium_score = min(
    100,
    total_calcium_mg / (required_calcium_mg_c + required_calcium_mg_m + required_calcium_mg_w + required_calcium_mg_o) * 100
)

iron_score = min(
    100,
    total_iron_mg / (required_iron_mg_c + required_iron_mg_m + required_iron_mg_w + required_iron_mg_o) * 100
)

sodium_score = min(
    100,
    total_sodium_mg / (required_sodium_mg_c + required_sodium_mg_m + required_sodium_mg_w + required_sodium_mg_o) * 100
)

zinc_score = min(
    100,
    total_zinc_mg / (required_zinc_mg_c + required_zinc_mg_m + required_zinc_mg_w + required_zinc_mg_o) * 100
)

vitaminC_score = min(
    100,
    total_vitaminC_mg / (required_vitaminC_mg_c + required_vitaminC_mg_m + required_vitaminC_mg_w + required_vitaminC_mg_o) * 100
)

vitaminB12_score = min(
    100,
    total_vitaminB12_ug / (required_vitaminB12_ug_c + required_vitaminB12_ug_m + required_vitaminB12_ug_w + required_vitaminB12_ug_o) * 100
)

vitaminA_score = min(
    100,
    total_vitaminA_ug / (required_vitaminA_ug_c + required_vitaminA_ug_m + required_vitaminA_ug_w + required_vitaminA_ug_o) * 100
)

vitaminD_score = min(
    100,
    total_vitaminD_ug / (required_vitaminD_ug_c + required_vitaminD_ug_m + required_vitaminD_ug_w + required_vitaminD_ug_o) * 100
)

# Overall score uses the limiting nutrient
diet_score = min(carbohydrates_score, protein_score, fat_score, calcium_score, iron_score, sodium_score,
                zinc_score, vitaminC_score, vitaminB12_score, vitaminA_score, vitaminD_score)


# =========================================
# 5. CARBON AND FOOD OUTPUTS
# =========================================

st.header("3. Environmental and food outputs")

a, b, c = st.columns(3)

a.metric(
    "Annual emissions",
    f"{total_emissions:,.0f} tCO2e"
)

b.metric(
    "Annual edible food",
    f"{total_food:,.0f} tonnes"
)

c.metric(
    "Dietary adequacy score",
    f"{diet_score:.1f}%"
)


production_df = pd.DataFrame({
    "Production": list(food_production.keys()),
    "Food produced (t/year)": list(food_production.values())
})

st.subheader("Food production by system")

st.dataframe(
    production_df,
    use_container_width=True,
    hide_index=True
)

st.subheader("Population dietary requirements")

d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11 = st.columns(11)

with d1:
    st.write("**Carbohydrate adequacy**")
    st.progress(carbohydrates_score / 100)
    st.write(f"{carbohydrates_score:.1f}% of annual carbohydrates requirements")

with d2:
    st.write("**Protein adequacy**")
    st.progress(protein_score / 100)
    st.write(f"{protein_score:.1f}% of annual protein requirements")

with d3:
    st.write("**Fat adequacy**")
    st.progress(fat_score / 100)
    st.write(f"{fat_score:.1f}% of annual fat requirements")

with d4:
    st.write("**Calcium adequacy**")
    st.progress(calcium_score / 100)
    st.write(f"{calcium_score:.1f}% of annual calcium requirements")

with d5:
    st.write("**Iron adequacy**")
    st.progress(iron_score / 100)
    st.write(f"{iron_score:.1f}% of annual iron requirements")

with d6:
    st.write("**Sodium adequacy**")
    st.progress(sodium_score / 100)
    st.write(f"{sodium_score:.1f}% of annual sodium requirements")

with d7:
    st.write("**Zinc adequacy**")
    st.progress(zinc_score / 100)
    st.write(f"{zinc_score:.1f}% of annual zinc requirements")

with d8:
    st.write("**Vitamin C adequacy**")
    st.progress(vitaminC_score / 100)
    st.write(f"{vitaminC_score:.1f}% of annual vitamin C requirements")

with d9:
    st.write("**Vitamin B12 adequacy**")
    st.progress(vitaminB12_score / 100)
    st.write(f"{vitaminB12_score:.1f}% of annual vitamin B12 requirements")

with d10:
    st.write("**Vitamin A adequacy**")
    st.progress(vitaminA_score / 100)
    st.write(f"{vitaminA_score:.1f}% of annual vitamin A requirements")

with d11:
    st.write("**Vitamin D adequacy**")
    st.progress(vitaminD_score / 100)
    st.write(f"{vitaminD_score:.1f}% of annual vitamin D requirements")

st.caption(
    "The dietary score is the lower of energy and protein "
    "adequacy. A score of 100% means both modelled requirements "
    "are met in aggregate; it does not establish a balanced diet."
)

if diet_score >= 100:
    st.success(
        "The modelled production meets all modelled "
        "dietary requirements."
    )
else:
    st.warning(
        "The modelled production does not meet all "
        "modelled dietary requirements."
    )

# =========================================
# 7. COMPARE PRODUCTION SYSTEMS
# =========================================

st.header("5. Compare land-use trade-offs")

chart_choice = st.selectbox(
    "Choose an output to compare",
    [
        "Emissions (tCO2e/year)",
        "Food (tonnes/year)",
        "Protein (kg/year)",
        "Carbohydrates (kg/year)",
        "Protein (kg/year)",
        "Fat (kg/year)",
        "Calcium (mg/year)",
        "Iron (mg/year)",
        "Sodium (mg/year)",
        "Zinc (mg/year)",
        "Vitamin C (mg/year)",
        "Vitamin B12 (ug/year)",
        "Vitamin A (ug/year)",
        "Vitamin D (ug/year)"
    ]
)

chart_df = df.set_index("Production")[[chart_choice]]

st.bar_chart(chart_df)


st.subheader("Detailed production results")

st.dataframe(
    df[
        [
            "Production",
            "Food (tonnes/year)",
            "Emissions (tCO2e/year)"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# =========================================
# 8. MODEL EQUATIONS
# =========================================

with st.expander("How the calculations work"):

    st.markdown("""

    **Annual emissions**

    Emissions = Food × Emissions intensity for each production

    **Dietary adequacy**

    Nutrient adequacy = Nutrient supply / Population requirement

    **Overall dietary score**

    Score = Minimum of energy adequacy and protein adequacy,
    capped at 100%.
    """)

    st.markdown("""
    **Limitations**

    - The model assumes all production is edible and available
      to the target population.
    - It excludes imports, exports, food waste and post-harvest losses.
    - It does not yet model soil carbon changes, land-use change,
      differences in production systems or changes over time.
    - It does not assess micronutrients or dietary diversity.
    - It is a very limited selection of food.
    - It doesnt account for vitamins that may be sourced outside of diet,
      such as vitamin D from sunlight.
    """)