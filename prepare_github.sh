#!/bin/bash
# GitHub Preparation Script
# This script helps prepare your project for GitHub

echo "🚀 Preparing Collaboration Suite for GitHub..."
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Copy .gitignore if needed
if [ ! -f ".gitignore" ]; then
    echo "⚠️  No .gitignore found!"
else
    echo "✅ .gitignore exists"
fi

# Check for LICENSE
if [ ! -f "LICENSE" ]; then
    echo "⚠️  No LICENSE found"
else
    echo "✅ LICENSE exists"
fi

# Check for README.md
if [ ! -f "README.md" ]; then
    echo "⚠️  No README.md found"
else
    echo "✅ README.md exists"
fi

echo ""
echo "📊 Repository Statistics:"
echo "---"
echo "Python files: $(find . -name '*.py' -not -path './venv/*' -not -path './__pycache__/*' | wc -l)"
echo "Total lines of code: $(find . -name '*.py' -not -path './venv/*' -not -path './__pycache__/*' -exec wc -l {} + | tail -1 | awk '{print $1}')"
echo ""

echo "📋 Files to be committed:"
echo "---"
git add --dry-run . 2>/dev/null | head -20
echo "... (use 'git add .' to stage all files)"
echo ""

echo "🗑️  Optional: Clean up internal documentation?"
echo "The following files are internal development docs:"
echo "  - FIXES_APPLIED*.md"
echo "  - SOLUTION.md"
echo "  - FIX_COMPLETE.md"
echo "  - CRITICAL_FIXES_VIDEO_RELAY.md"
echo "  - PORT_BINDING_FIX.md"
echo ""
read -p "Remove these files? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing internal docs..."
    rm -f FIXES_APPLIED.md FIXES_APPLIED_V2.md IMPORT_FIXES.md
    rm -f SOLUTION.md FIX_COMPLETE.md ALL_FIXES_COMPLETE.md
    rm -f CRITICAL_FIXES_VIDEO_RELAY.md PORT_BINDING_FIX.md
    rm -f GUI_TROUBLESHOOTING.md GUI_CLIENT_README.md QUICK_START.md
    echo "✅ Internal docs removed"
else
    echo "⏭️  Keeping all documentation"
fi

echo ""
echo "📝 Next Steps:"
echo "---"
echo "1. Review files: git status"
echo "2. Add files: git add ."
echo "3. Commit: git commit -m 'Initial commit: LAN Collaboration Suite'"
echo "4. Create GitHub repository at: https://github.com/new"
echo "5. Add remote: git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "6. Push: git push -u origin main"
echo ""
echo "See GITHUB_SETUP.md for detailed instructions!"
echo ""
