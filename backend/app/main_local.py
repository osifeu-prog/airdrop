from fastapi import FastAPI

app = FastAPI()

@app.get('/public/health')
async def health_check():
    return {"status": "ok"}

@app.post('/public/invite/create')
async def create_invite(created_by: str, role: str):
    return {"invite_id": "test-invite-123"}

@app.post('/public/invite/use')
async def use_invite(invite_id: str, user_id: str):
    return {"status": {"role": "leader", "invited_by": "osif", "joined_at": "now"}}

@app.get('/public/progress')
async def progress():
    return {"progress": 42}
