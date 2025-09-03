# HACS Setup Instructions

This document contains instructions for setting up this repository to pass HACS validation.

## GitHub Repository Configuration

To fix the HACS validation failures, the following needs to be configured on the GitHub repository:

### 1. Repository Description

Set the repository description to:
```
Home Assistant custom integration for Homevolt Energy Management System (EMS)
```

**How to set:**
1. Go to the repository on GitHub
2. Click the gear icon (⚙️) next to "About" 
3. Add the description above
4. Save changes

### 2. Repository Topics

Add the following topics to the repository:
- `home-assistant`
- `hacs`
- `custom-integration`
- `homevolt`
- `energy-management`
- `battery`
- `solar`

**How to set:**
1. Go to the repository on GitHub
2. Click the gear icon (⚙️) next to "About"
3. In the "Topics" section, add the topics listed above
4. Save changes

### 3. Verify HACS Validation

After making these changes:
1. Go to Actions tab in GitHub
2. Re-run the HACS validation workflow
3. Verify all checks pass

## Current HACS Validation Status

Last validation errors:
- ❌ Repository has no description
- ❌ Repository has no valid topics
- ✅ Category: integration
- ✅ Validation information completed
- ✅ Validation issues completed
- ✅ Validation archived completed
- ✅ Validation hacsjson completed
- ✅ Validation integration_manifest completed

## Integration Status

The integration itself is fully functional and ready for HACS distribution once the repository configuration is complete.
