"""
Test script for Vector Search functionality in Astra DB
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.astra_helper import get_db_helper


def test_vector_search():
    """Test semantic vector search for menu items"""
    print("=" * 80)
    print("VECTOR SEARCH TEST - Semantic Meal Recommendations")
    print("=" * 80)
    
    db = get_db_helper()
    
    # Test 1: Search for healthy protein
    print("\n1. SEMANTIC SEARCH: 'healthy protein for diabetic patient'")
    print("-" * 80)
    
    results = db.vector_search_menu_items(
        query_text="healthy protein for diabetic patient",
        dietary_restrictions=["diabetic", "low-sodium"],
        allergies=["peanuts"],
        limit=5
    )
    
    print(f"\n   Found {len(results)} matching meals")
    
    for i, item in enumerate(results, 1):
        print(f"\n   {i}. {item.get('name')}")
        print(f"      Description: {item.get('description', 'N/A')}")
        print(f"      Calories: {item.get('calories')} kcal")
        print(f"      Protein: {item.get('protein_g')}g | Carbs: {item.get('carbs_g')}g | Fat: {item.get('fat_g')}g")
        print(f"      Category: {item.get('category')}")
        
        # Show dietary tags
        dietary_tags = item.get('dietary_tags', [])
        if dietary_tags:
            print(f"      Dietary Tags: {', '.join(dietary_tags)}")
        
        # Show similarity score if available
        similarity = item.get('$similarity')
        if similarity:
            print(f"      Similarity Score: {similarity:.3f}")
    
    # Test 2: Search for vegetarian breakfast
    print("\n\n2. SEMANTIC SEARCH: 'vegetarian breakfast high fiber'")
    print("-" * 80)
    
    results = db.vector_search_menu_items(
        query_text="vegetarian breakfast high fiber",
        dietary_restrictions=["vegetarian"],
        allergies=None,
        limit=5
    )
    
    print(f"\n   Found {len(results)} matching meals")
    
    for i, item in enumerate(results, 1):
        print(f"\n   {i}. {item.get('name')}")
        print(f"      Category: {item.get('category')}")
        print(f"      Calories: {item.get('calories')} kcal | Fiber: {item.get('fiber_g', 'N/A')}g")
        
        dietary_tags = item.get('dietary_tags', [])
        if dietary_tags:
            print(f"      Tags: {', '.join(dietary_tags)}")
    
    # Test 3: Search with allergen exclusion
    print("\n\n3. SEMANTIC SEARCH: 'light salad' (exclude shellfish)")
    print("-" * 80)
    
    results = db.vector_search_menu_items(
        query_text="light salad fresh vegetables",
        dietary_restrictions=None,
        allergies=["shellfish", "peanuts"],
        limit=5
    )
    
    print(f"\n   Found {len(results)} matching meals")
    
    for i, item in enumerate(results, 1):
        print(f"\n   {i}. {item.get('name')}")
        print(f"      Calories: {item.get('calories')} kcal")
        
        allergens = item.get('allergens', [])
        if allergens:
            print(f"      Allergens: {', '.join(allergens)}")
        else:
            print(f"      Allergens: None")
    
    # Test 4: Search for low-carb options
    print("\n\n4. SEMANTIC SEARCH: 'low carb keto friendly meal'")
    print("-" * 80)
    
    results = db.vector_search_menu_items(
        query_text="low carb keto friendly meal",
        dietary_restrictions=["low-carb"],
        allergies=None,
        limit=5
    )
    
    print(f"\n   Found {len(results)} matching meals")
    
    for i, item in enumerate(results, 1):
        print(f"\n   {i}. {item.get('name')}")
        print(f"      Carbs: {item.get('carbs_g')}g | Protein: {item.get('protein_g')}g | Fat: {item.get('fat_g')}g")
        print(f"      Net Carbs: ~{item.get('carbs_g', 0) - item.get('fiber_g', 0)}g")
    
    # Test 5: General search without restrictions
    print("\n\n5. SEMANTIC SEARCH: 'comfort food chicken'")
    print("-" * 80)
    
    results = db.vector_search_menu_items(
        query_text="comfort food chicken savory",
        dietary_restrictions=None,
        allergies=None,
        limit=5
    )
    
    print(f"\n   Found {len(results)} matching meals")
    
    for i, item in enumerate(results, 1):
        print(f"\n   {i}. {item.get('name')}")
        print(f"      Category: {item.get('category')}")
        print(f"      Description: {item.get('description', 'N/A')[:60]}...")
    
    print("\n" + "=" * 80)
    print("✅ VECTOR SEARCH TESTS COMPLETED")
    print("=" * 80)
    
    print("\n💡 KEY BENEFITS OF VECTOR SEARCH:")
    print("   - Semantic understanding (not just keyword matching)")
    print("   - Finds similar meals even with different words")
    print("   - Respects dietary restrictions and allergen exclusions")
    print("   - Ranks results by relevance")
    print("   - Natural language queries")


if __name__ == "__main__":
    test_vector_search()
