# Check list for fresh startup

## User management related

### Admin (`superuser`)

- [ ] Login with the default admin account:
  - email: `admin@example.com`
  - password: `Waseda2025`
- [ ] Create a new admin account with your own email address
- [ ] Delete the default admin account

### Teachers (`staff`)

- [ ] Add permission group for teacher with following items, name this group e.g., `Course Teacher` (https://app.awade.gec.waseda.ac.jp/admin/auth/group/)
  - LLM Caller | api request | Can manage APl requests with limited visibility
  - LLM Caller | batch processing | Can manage batch processing requests with limited visibility
  - Users | course | Can manage courses with limited visibility
  - Users | user | Can manage users with limited visibility
- [ ] Add users (https://app.awade.gec.waseda.ac.jp/admin/users/user/)
  - [ ] Set teachers as staff (so they can login to the admin page)
  - [ ] Add teachers to the permission group `Course Teacher` (so they have the permission to manage users, and use the batch processing features)

## LLM models related

- [ ] Add LLM models (https://app.awade.gec.waseda.ac.jp/admin/llm_caller/llmmodel/)
- [ ] Add API keys (https://app.awade.gec.waseda.ac.jp/admin/llm_caller/apikey/)
- [ ] Add prompts in LLM configs (https://app.awade.gec.waseda.ac.jp/admin/llm_caller/llmconfig/)
- [ ] Add quota for individual LLM models (`unlimited` if non existent) (https://app.awade.gec.waseda.ac.jp/admin/llm_caller/quotaconfig/)
