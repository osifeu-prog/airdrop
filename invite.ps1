# -------------------------------
# invite.ps1 - Auto Invite Creator & User
# -------------------------------

# הגדר פרמטרים
$server = "http://127.0.0.1:8000"
$created_by = "osif"
$role = "leader"
$user_id = "friend1"

try {
    # 1️⃣ צור invite חדש
    $createResponse = Invoke-RestMethod `
        -Uri "$server/public/invite/create?created_by=$created_by&role=$role" `
        -Method POST

    Write-Host "✅ Invite created:"
    $createResponse | Format-Table

    # 2️⃣ קח את invite_id מהתשובה
    $invite_id = $createResponse.invite_id

    # 3️⃣ השתמש ב-invite עבור user
    $useResponse = Invoke-RestMethod `
        -Uri "$server/public/invite/use?invite_id=$invite_id&user_id=$user_id" `
        -Method POST

    # 4️⃣ הצג את התוצאה
    Write-Host "`n✅ Invite used:"
    $useResponse | Format-Table

} catch {
    Write-Host "`n❌ Error occurred:"
    Write-Host $_.Exception.Message
}
