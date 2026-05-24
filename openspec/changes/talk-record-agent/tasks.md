## 1. Backend Model & Schema

- [x] 1.1 Create TalkRecord SQLAlchemy model (id, student_name, student_id, situation, conversation_record, risk_level, follow_up_advice, parent_advice, status, created_by, timestamps)
- [x] 1.2 Create TalkRecordStatus enum (DRAFT, WAITING_APPROVAL, APPROVED)
- [x] 1.3 Create Pydantic schemas (GenerateTalkRecordRequest, TalkRecordResponse, TalkRecordListItem)
- [x] 1.4 Register TalkRecord in models/__init__.py

## 2. Backend Prompt & Task

- [x] 2.1 Create prompts/talk_record.py with talk_record generation prompt (4 outputs: conversation_record, risk_level, follow_up_advice, parent_advice)
- [x] 2.2 Update prompts/__init__.py to export build_talk_record_prompt
- [x] 2.3 Create tasks/talk_record_task.py with generate_talk_record_task function (accepts student info + situation + counselor profile)
- [x] 2.4 Inject counselor profile into talk record prompt (name, college)

## 3. Backend API

- [x] 3.1 Create api/talk_records.py with POST /api/talk-records/generate, GET /api/talk-records, GET /api/talk-records/{id}, PUT /api/talk-records/{id}/approve, PUT /api/talk-records/{id}/reject
- [x] 3.2 Register talk_records router in main.py
- [x] 3.3 Load CounselorProfile in generate endpoint and pass to task

## 4. Frontend API & Store

- [x] 4.1 Add talk record types and API functions to frontend API module
- [x] 4.2 Create talk record Pinia store (generate, approve, reject, fetchList, fetchOne)

## 5. Frontend Pages & Components

- [x] 5.1 Create TalkRecordGenerator.vue page (student info form + situation textarea + result display)
- [x] 5.2 Add /talk-record route to router
- [x] 5.3 Add navigation between notice generator and talk record pages

## 6. Verification

- [x] 6.1 Test generate talk record via API (curl)
- [x] 6.2 Test approve/reject workflow
- [x] 6.3 Test frontend UI renders and connects to backend
- [x] 6.4 Test with counselor profile configured (verify real name in output)
- [x] 6.5 Test backward compatibility (notices still work)
