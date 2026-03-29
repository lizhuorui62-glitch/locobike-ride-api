
### 2. AI_REFLECTION.md


# AI Usage Reflection for LocoBike Ride API
This document details the AI tools used, prompts, AI-generated weaknesses, and manual improvements for the project, as required by the take-home test.

## 1. AI Tools Used
- **Primary Tool**: ChatGPT 4o (for core code skeleton, logic draft)
- **Secondary Tool**: GitHub Copilot (for code autocomplete, syntax correction, naming suggestions)
- **Auxiliary Tool**: Claude 3 Sonnet (for reviewing pricing logic edge cases)

## 2. Key Prompts/Instructions Given
### To ChatGPT 4o:
> Build a FastAPI backend for a bike ride service with SQLite, implement 4 API endpoints: POST /ride/start, POST /ride/end, GET /ride/{id}, GET /ride/{id}/cost. Follow pricing rules: $5 unlock fee, 15 mins free, $1 per 5 mins after, $25 daily cap. Use SQLAlchemy for ORM, Pydantic for validation, add error handling for non-existent ride ID, duplicate end ride, uncompleted ride cost query. Organize code by models/schemas/services/main.

### To Copilot:
> Optimize FastAPI route error handling, add UTC time for ride start/end, implement ceil for extra minutes calculation in pricing logic, add database timestamp fields (created_at/updated_at).

## 3. Mistakes/Weaknesses/Blind Spots in AI-generated Output
1. **Pricing Logic Errors**: ChatGPT initially calculated extra minutes with `floor()` instead of `ceil()` (e.g., 16 mins extra was 0 units instead of 1), and forgot to apply the $25 daily cap to the total cost.
2. **Time Zone Issue**: AI used local time instead of UTC for ride start/end time (critical for global service consistency).
3. **Incomplete Error Handling**: Missing validation for "end a non-existent ride" and "duplicate end a completed ride", only basic 404 was added.
4. **Database Model Defects**: No `is_completed` field (hard to judge ride status), no `created_at/updated_at` time stamps (bad for traceability).
5. **Code Structure**: AI mixed business logic (pricing calculation) with route code (main.py) instead of encapsulating in a separate services.py (violates separation of concerns).
6. **Edge Case Ignorance**: Did not handle "calculate cost for an uncompleted ride" (returned empty cost instead of throwing an exception).

## 4. Manual Verification/Fix/Improvement
1. **Fixed Pricing Logic**: Replaced `floor()` with `ceil()` for extra 5-minute units, added `min(pre_cap_total, 25)` to apply daily cap, added a `daily_cap_applied` flag for transparency.
2. **Time Standardization**: Modified all datetime fields to use `datetime.utcnow()` (UTC time) for global service compatibility.
3. **Enhanced Error Handling**: Added detailed HTTP exceptions (400/404) with specific error messages for all abnormal scenarios (non-existent ride, duplicate end, uncompleted cost query).
4. **Optimized Database Model**: Added `is_completed` boolean field, `created_at/updated_at` time stamps, set default values for `unlock_fee` (5.0).
5. **Refactored Code Structure**: Extracted all business logic (ride start/end, cost calculation) to `services.py`, making main.py only for route registration (separation of concerns, easy to maintain).
6. **Added Edge Case Handling**: Explicitly throw an error when calculating cost for an uncompleted ride, added validation for positive ride ID (Pydantic `gt=0`).
7. **Engineering Polishing**: Added a health check endpoint (`/`), added API docs (Swagger/ReDoc), wrote a detailed README with curl test examples, added unit tests for core logic.
8. **Dependency Management**: Created a precise `requirements.txt` with fixed versions (avoid environment inconsistency).

## 5. Key Takeaways from AI-assisted Development
AI is a powerful force multiplier for rapid code skeleton generation, but it lacks **engineering judgment** and **edge case awareness** for real-world applications. Critical business logic (e.g., pricing) and system design (e.g., code structure, time zone) must be manually verified and optimized. The final code ownership is entirely mine, as all AI-generated defects were fixed and the project was polished to meet production-level code quality requirements.
