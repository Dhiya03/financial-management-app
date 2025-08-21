"""
Category operations and auto-categorization manager
"""

import logging
from typing import Dict, List, Optional

from config import CATEGORY_KEYWORDS

class CategoryManager:
    """Manages category operations and auto-categorization"""
    
    def __init__(self):
        from managers.data_manager import data_manager
        self.app_data = data_manager.get_data()
    
    def get_all_categories(self) -> Dict[str, List[str]]:
        """Get all categories grouped by type"""
        return self.app_data.categories
    
    def get_flat_category_list(self) -> List[str]:
        """Get flat list of all categories"""
        categories = []
        for group_categories in self.app_data.categories.values():
            categories.extend(group_categories)
        return categories
    
    def add_category(self, group: str, category_name: str) -> tuple[bool, str]:
        """Add a new category to a group"""
        try:
            # Validate input
            if not category_name or not category_name.strip():
                return False, "Category name cannot be empty"
            
            # Check if category already exists
            if category_name in self.get_flat_category_list():
                return False, "Category already exists"
            
            # Add to appropriate group
            if group not in self.app_data.categories:
                self.app_data.categories[group] = []
            
            self.app_data.categories[group].append(category_name)
            
            # Save changes
            from managers.data_manager import data_manager
            if data_manager.save():
                logging.info(f"Added category: {category_name} to group: {group}")
                return True, "Category added successfully"
            else:
                return False, "Failed to save category"
                
        except Exception as e:
            logging.error(f"Error adding category: {e}")
            return False, f"Error adding category: {str(e)}"
    
    def remove_category(self, category_name: str) -> tuple[bool, str]:
        """Remove a category"""
        try:
            # Find and remove category
            for group, categories in self.app_data.categories.items():
                if category_name in categories:
                    categories.remove(category_name)
                    
                    from managers.data_manager import data_manager
                    if data_manager.save():
                        logging.info(f"Removed category: {category_name}")
                        return True, "Category removed successfully"
                    else:
                        return False, "Failed to save changes"
            
            return False, "Category not found"
            
        except Exception as e:
            logging.error(f"Error removing category: {e}")
            return False, f"Error removing category: {str(e)}"
    
    def auto_categorize_transaction(self, description: str) -> Optional[str]:
        """Auto-categorize transaction based on description"""
        try:
            if not description:
                return None
            
            description_upper = description.upper()
            keywords = self.app_data.settings.get('category_keywords', CATEGORY_KEYWORDS)
            
            # Score each category based on keyword matches
            category_scores = {}
            
            for category, category_keywords in keywords.items():
                score = 0
                for keyword in category_keywords:
                    if keyword.upper() in description_upper:
                        # Longer keywords get higher scores
                        score += len(keyword)
                
                if score > 0:
                    category_scores[category] = score
            
            # Return category with highest score
            if category_scores:
                best_category = max(category_scores, key=category_scores.get)
                logging.info(f"Auto-categorized '{description}' as '{best_category}'")
                return best_category
            
            return None
            
        except Exception as e:
            logging.error(f"Error in auto-categorization: {e}")
            return None
    
    def add_keyword_rule(self, category: str, keyword: str) -> tuple[bool, str]:
        """Add a keyword rule for auto-categorization"""
        try:
            keywords = self.app_data.settings.get('category_keywords', {})
            
            if category not in keywords:
                keywords[category] = []
            
            if keyword.upper() not in [k.upper() for k in keywords[category]]:
                keywords[category].append(keyword)
                self.app_data.settings['category_keywords'] = keywords
                
                from managers.data_manager import data_manager
                if data_manager.save():
                    return True, "Keyword rule added successfully"
                else:
                    return False, "Failed to save keyword rule"
            else:
                return False, "Keyword already exists for this category"
                
        except Exception as e:
            logging.error(f"Error adding keyword rule: {e}")
            return False, f"Error adding keyword rule: {str(e)}"
    
    def get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for a specific category"""
        keywords = self.app_data.settings.get('category_keywords', {})
        return keywords.get(category, [])
    
    def update_category_name(self, old_name: str, new_name: str) -> tuple[bool, str]:
        """Update category name"""
        try:
            # Check if new name already exists
            if new_name in self.get_flat_category_list():
                return False, "Category name already exists"
            
            # Find and update category
            for group, categories in self.app_data.categories.items():
                if old_name in categories:
                    index = categories.index(old_name)
                    categories[index] = new_name
                    
                    # Update keywords mapping
                    keywords = self.app_data.settings.get('category_keywords', {})
                    if old_name in keywords:
                        keywords[new_name] = keywords.pop(old_name)
                        self.app_data.settings['category_keywords'] = keywords
                    
                    from managers.data_manager import data_manager
                    if data_manager.save():
                        logging.info(f"Updated category name from '{old_name}' to '{new_name}'")
                        return True, "Category updated successfully"
                    else:
                        return False, "Failed to save changes"
            
            return False, "Category not found"
            
        except Exception as e:
            logging.error(f"Error updating category: {e}")
            return False, f"Error updating category: {str(e)}"
