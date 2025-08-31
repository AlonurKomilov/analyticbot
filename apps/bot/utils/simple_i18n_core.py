"""Custom I18N Core for AnalyticBot"""
from pathlib import Path


class SimpleI18nCore:
    """Simple I18N implementation that loads .ftl files directly"""
    
    def __init__(self, path_template: str):
        self.path_template = path_template
        self.locales: dict[str, dict[str, str]] = {}
        self._loaded = False
    
    def find_locales(self) -> dict[str, dict[str, str]]:
        """Find and load all locale files"""
        locales = {}
        # Fix: Use dummy replacement to get correct parent path
        base_path = Path(self.path_template.replace("{locale}", "dummy")).parent
        
        if not base_path.exists():
            print(f"I18N: Locale base path does not exist: {base_path}")
            return {}
            
        for locale_dir in base_path.iterdir():
            if locale_dir.is_dir() and not locale_dir.name.startswith('_'):
                locale_name = locale_dir.name
                ftl_files = list(locale_dir.glob("*.ftl"))
                
                if ftl_files:
                    locale_data = {}
                    for ftl_file in ftl_files:
                        try:
                            content = ftl_file.read_text(encoding='utf-8')
                            # Parse simple key = value pairs from ftl content
                            locale_data.update(self._parse_ftl_content(content))
                            print(f"I18N: Loaded {ftl_file} with {len(locale_data)} keys")
                        except Exception as e:
                            print(f"I18N: Error loading {ftl_file}: {e}")
                    
                    if locale_data:
                        locales[locale_name] = locale_data
                        print(f"I18N: Locale '{locale_name}' loaded with {len(locale_data)} total keys")
        
        return locales
    
    def _parse_ftl_content(self, content: str) -> dict[str, str]:
        """Parse FTL content and extract key-value pairs"""
        data = {}
        current_key = None
        current_value = []
        
        for line in content.split('\n'):
            original_line = line
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
                
            # Check if this is a key line
            if '=' in line and not line.startswith(' ') and not line.startswith('\t'):
                # Save previous key if exists
                if current_key:
                    data[current_key] = '\n'.join(current_value).strip()
                
                # Start new key
                key, value = line.split('=', 1)
                current_key = key.strip()
                current_value = [value.strip()] if value.strip() else []
                
            elif current_key and (original_line.startswith('    ') or original_line.startswith('\t')):
                # This is a continuation of the current value (indented lines)
                current_value.append(original_line.strip())
        
        # Don't forget the last key
        if current_key:
            data[current_key] = '\n'.join(current_value).strip()
            
        return data
    
    def get(self, key: str, locale: str = 'en', **kwargs) -> str:
        """Get localized string"""
        if not self._loaded:
            self.locales = self.find_locales()
            self._loaded = True
        
        # Get the translation
        translation = self.locales.get(locale, {}).get(key)
        
        # Fallback to English if not found
        if not translation and locale != 'en':
            translation = self.locales.get('en', {}).get(key)
        
        # Return key if no translation found
        if not translation:
            return key
            
        # Simple parameter substitution
        result = translation
        for param_key, param_value in kwargs.items():
            placeholder = "{" + f" ${param_key}" + " }"
            result = result.replace(placeholder, str(param_value))
            
        return result
