# Overview

CyberNav: Campus Route AI is a Streamlit-based web application that provides intelligent campus navigation with AI-powered assistance. The application combines advanced pathfinding algorithms with Google's Gemini AI to deliver optimal route planning and interactive campus guidance. Users can find paths between various points of interest on campus using different algorithms (A*, Dijkstra, BFS, DFS) with multiple heuristics, while also accessing an AI assistant for campus-related queries and information.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application with responsive layout
- **UI Design**: Cyberpunk dark mode theme with neon accent colors (#00ffff, electric blue, neon green)
- **Layout Pattern**: Tabbed interface with two main sections:
  - Route Planner tab for navigation functionality
  - AI & Analysis tab for AI assistant and performance analytics
- **Interactive Components**: Folium maps integrated via streamlit-folium for real-time route visualization

## Backend Architecture
- **Core Logic Separation**: Modular design with distinct responsibilities:
  - `pathfinding.py`: Graph algorithms and route calculation engine
  - `gemini_integration.py`: AI assistant functionality and campus knowledge base
  - `app.py`: UI orchestration and user interaction handling
- **Graph Processing**: OSMnx library for handling OpenStreetMap data and campus topology
- **Algorithm Engine**: Multiple pathfinding implementations (A*, Dijkstra, BFS, DFS) with configurable heuristics

## Data Storage Solutions
- **Graph Data**: Campus map stored as OSM (OpenStreetMap) XML file
- **Configuration**: Environment variables loaded from .env file for API keys
- **POI Database**: Hardcoded dictionary of campus points of interest with coordinates
- **Session State**: Streamlit session management for maintaining user interactions

## Authentication and Authorization
- **API Security**: Google Gemini API key authentication via environment variables
- **Access Control**: No user authentication required - public campus navigation tool

# External Dependencies

## Third-party Services
- **Google Gemini AI**: Conversational AI for campus assistance and query handling
- **OpenStreetMap**: Campus topology and routing graph data source

## Key Libraries and Frameworks
- **streamlit**: Web application framework and UI components
- **streamlit-folium**: Interactive map integration
- **osmnx**: OpenStreetMap data processing and graph manipulation
- **networkx**: Graph algorithms and network analysis
- **folium**: Interactive map visualization and route rendering
- **pandas**: Data manipulation and analysis for performance metrics
- **google-genai**: Official Google Gemini AI client library

## Data Processing Dependencies
- **heapq**: Priority queue implementation for pathfinding algorithms
- **math**: Mathematical calculations for distance heuristics
- **difflib**: String similarity matching for location name normalization
- **re**: Regular expression processing for text normalization