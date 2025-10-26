#!/bin/bash

# Fix relative imports to use path aliases
# Run from: apps/frontend/

echo "🔧 Fixing imports in frontend..."
cd /home/abcdeveloper/projects/analyticbot/apps/frontend/src

# 1. Fix theme imports
echo "  - Fixing theme imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/theme\/designTokens['\"]|from '@theme/designTokens'|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/theme\/designTokens['\"]|from '@theme/designTokens'|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/theme\/designTokens['\"]|from '@theme/designTokens'|g" {} \;

# 2. Fix contexts imports
echo "  - Fixing context imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/contexts\/AuthContext['\"]|from '@/contexts/AuthContext'|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/contexts\/AuthContext['\"]|from '@/contexts/AuthContext'|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/contexts\/AuthContext['\"]|from '@/contexts/AuthContext'|g" {} \;

# 3. Fix shared components imports
echo "  - Fixing shared component imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/EmptyState['\"]|from '@shared/components/feedback/EmptyState'|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/EmptyState['\"]|from '@shared/components/feedback/EmptyState'|g" {} \;

# 4. Fix __mocks__ imports
echo "  - Fixing __mocks__ imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/\.\.\/__mocks__\/constants['\"]|from '@/__mocks__/constants'|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/__mocks__\/|from '@/__mocks__/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/__mocks__\/|from '@/__mocks__/|g" {} \;

# 5. Fix types imports
echo "  - Fixing types imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/types\/|from '@types/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/types\/|from '@types/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/types\/|from '@types/|g" {} \;

# 6. Fix validation imports
echo "  - Fixing validation imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/validation\/|from '@/validation/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/validation\/|from '@/validation/|g" {} \;

# 7. Fix utils imports
echo "  - Fixing utils imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/utils\/|from '@shared/utils/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/utils\/|from '@shared/utils/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/utils\/|from '@shared/utils/|g" {} \;

# 8. Fix store/slices imports
echo "  - Fixing store imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/store\/slices\/|from '@store/slices/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/store\/slices\/|from '@store/slices/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/store\/slices\/|from '@store/slices/|g" {} \;

# 9. Fix config imports
echo "  - Fixing config imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/config\/|from '@config/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/config\/|from '@config/|g" {} \;

# 10. Fix api imports
echo "  - Fixing api imports..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/api\/|from '@api/|g" {} \;

find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  "s|from ['\"]\.\.\/\.\.\/\.\.\/api\/|from '@api/|g" {} \;

echo ""
echo "✅ Import fixes complete!"
echo ""
echo "📊 Checking remaining relative imports..."
REMAINING=$(grep -r "from ['\"]\.\./" . --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v node_modules | wc -l)
echo "   Remaining relative imports: $REMAINING"
echo ""
echo "🔍 Next: Run 'npm run type-check' to validate"
