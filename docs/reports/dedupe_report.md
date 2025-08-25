# Dedupe Plan

Generated: August 24, 2025

## Summary

The deduplication scanner analyzed the workspace and found:

### Exact Duplicates (Same Content, Same Hash)
- **Total groups**: 2,404 (including node_modules)
- **Core codebase groups**: 21 (excluding node_modules)

Key findings in the main codebase:
- Multiple API files duplicated between root and `apps/api/`
- Documentation reports duplicated between root and `docs/` directories  
- Configuration files spread across multiple locations
- Bot utilities duplicated between `apps/bot/` and root directories
- Migration files duplicated between `infra/db/` and root `migrations/`

### Same Name, Different Content
- **Total conflicts**: 14,702 (including node_modules)  
- **Core codebase conflicts**: ~50+ (excluding node_modules)

Major naming conflicts:
- `__init__.py` files with different content across modules
- `config.py` files with different configurations 
- `main.py` files serving different purposes
- `.env` and `.gitignore` files with different settings
- Kubernetes YAML files duplicated between `infra/k8s/` and `infra/helm/`

## Canonicalization Strategy

Following the preference order:
1. `apps/api/*` → 2. `apps/bot/*` → 3. `apps/frontend/*` → 4. `core/*` → 5. `infra/*` → 6. `config/*` → 7. `scripts/*`

### Recommended Actions

**Phase 1: Exact Duplicates (Safe to Archive)**
- Move root-level duplicates to `archive/legacy_*` 
- Keep canonical versions in `apps/`, `core/`, or `infra/`
- Add compatibility imports where needed

**Phase 2: Same-Name Conflicts (Manual Review Required)**  
- Merge or rename conflicting files
- Consolidate configuration approaches
- Standardize module initialization

**Phase 3: Directory Structure Cleanup**
- Migrate remaining root-level files to canonical locations
- Update import paths and references
- Remove empty directories

## Files Generated
- `exact_duplicates.csv` - Groups of files with identical content
- `same_name_diff_content.csv` - Files with same names but different content

## Next Steps
1. Review exact duplicate groups for safe archival
2. Analyze same-name conflicts for consolidation strategy  
3. Create migration scripts with compatibility shims
4. Run tests after each batch of changes
