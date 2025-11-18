# GitHub Copilot Instructions - Sagittarius ENTJ App

## Project Context
This is a PySide6-based desktop application that can be packaged as an executable using PyInstaller.

## Coding Standards

### Python Style
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use docstrings for all classes and functions (Google style)
- Prefer f-strings for string formatting

### Code Organization
- Keep functions small and focused (max 50 lines)
- Use meaningful variable and function names
- Group related functionality into classes
- Separate UI logic from business logic

### PySide6 Best Practices
- Always use signal/slot connections for UI interactions
- Implement proper cleanup in `closeEvent` handlers
- Use `QThread` for long-running operations to avoid UI freezing
- Store UI strings as constants for easy localization

### Error Handling
- Always use try-except blocks for file I/O operations
- Log errors with context information
- Provide user-friendly error messages in the UI
- Never silently fail - always handle or propagate exceptions

## File Structure Guidelines

### Main Application File
- Entry point should be minimal
- Main logic in separate classes
- Use `if __name__ == "__main__":` guard

### Resource Files
- Keep all resources (images, icons, translations) in a dedicated folder
- Use Qt resource system (.qrc) for bundling

### Build Configuration
- Keep `.spec` file updated with all dependencies
- Document any special PyInstaller hooks needed
- Test executable on clean system before release

## Testing Requirements
- Write unit tests for business logic
- Test UI components manually
- Verify executable works on target OS
- Check for memory leaks in long-running operations

## Git Commit Guidelines
- Use conventional commits format:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `refactor:` for code restructuring
  - `docs:` for documentation
  - `build:` for build system changes
- Keep commits atomic and focused
- Write clear, descriptive commit messages

## Documentation
- Update README.md when adding new features
- Document all command-line arguments
- Include setup instructions for developers
- Document build process and dependencies

## Security
- Never hardcode sensitive data (API keys, passwords)
- Validate all user inputs
- Use secure file operations
- Follow principle of least privilege

## Performance
- Profile code before optimizing
- Use Qt's model/view architecture for large datasets
- Minimize UI updates and redraws
- Cache expensive computations when appropriate

## Design-First Approach

### Before Implementing Features
1. **Generate UML Design First**: Create PlantUML diagrams to visualize the architecture
   - Use PlantUML syntax for class diagrams, sequence diagrams, component diagrams
   - Show relationships between classes, interfaces, and modules
   - Include key methods and properties
   - Highlight design patterns being used

2. **Present Design for Approval**: 
   - Show the UML diagram(s) to explain the proposed solution
   - Explain the design decisions and trade-offs
   - List any new dependencies or changes to existing code
   - Wait for user confirmation before proceeding

3. **Implement After Confirmation**:
   - Only start coding after design approval
   - Follow the approved design closely
   - Document any deviations from the original design

### PlantUML Guidelines
- Use `@startuml` and `@enduml` tags
- Include meaningful class/component names
- Show inheritance with `<|--` and composition with `*--`
- Add notes to explain complex relationships
- Keep diagrams focused and readable

## When Implementing Changes
1. **Design First**: Generate UML diagrams and get approval
2. Understand the existing code structure first
3. Maintain consistency with current patterns
4. Test changes locally before committing
5. Update documentation if needed
6. Check that the executable still builds correctly

## Specific to This Project
- The main application file is `Sagittarius-ENTJ.py`
- Build script is `buildExe.ps1` (PowerShell)
- PyInstaller spec file is `Sagittarius-ENTJ.spec`
- Output executable goes to `executable/` directory
- Build artifacts in `build/` directory

## Do Not
- Don't modify the build output directories manually
- Don't commit compiled files or build artifacts
- Don't use platform-specific code without abstraction
- Don't introduce unnecessary dependencies
- Don't remove error handling to "simplify" code

## Preferred Libraries
- Use PySide6 for GUI (already in use)
- Use pathlib for file path operations
- Use logging module for debug output
- Use json/configparser for configuration files

## Questions to Ask Before Implementing
1. Does this change maintain cross-platform compatibility?
2. Will this affect the PyInstaller build process?
3. Are there any new dependencies that need to be documented?
4. Does this follow the existing code patterns?
5. Is proper error handling included?
