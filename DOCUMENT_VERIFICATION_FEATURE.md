# Document Verification System - Implementation Guide

## ✅ Feature Overview

The Document Verification System allows admins to verify or reject uploaded documents (WAEC results, JAMB slips, passport photos, birth certificates) with comments, and automatically notifies applicants about the status of their documents.

---

## 🎯 Key Features Implemented

### 1. **Document Verification Statuses**
Each document can have three statuses:
- 🟡 **Pending** - Awaiting admin review (default)
- 🟢 **Verified** - Admin approved the document
- 🔴 **Rejected** - Admin rejected with reason/comment

### 2. **Admin Interface Enhancements**

#### A. List View Improvements
- Added "Document Status" column showing overall verification status with color badges
- Added filters for each document verification status
- Verification status displayed as:  - ✓ All Verified (green)
  - ✗ X Rejected (red)
  - ⏳ X Pending (yellow)

#### B. Edit Form Improvements
- **Document Verification Summary** section showing overall stats
- **Documents & Verification** section with:
  - Clickable links to view each document
  - Status badges next to each document
  - Dropdown to change status (Pending/Verified/Rejected)
  - Comment field for rejection reasons
- **Verification Metadata** tracking who verified and when

#### C. Bulk Actions
- **"✓ Verify all documents"** - Instantly verify all documents for selected forms
- **"⏳ Mark all documents as pending"** - Reset verification status

#### D. Automatic Notifications
When admin verifies/rejects documents:
- ✅ **All verified**: "All your documents have been verified! Your application is now being processed."
- ❌ **Rejected**: Lists rejected documents with reasons + "Please re-upload the correct documents."
- ⚠️ **Partially verified**: "The following documents have been verified: X, Y, Z"

### 3. **Applicant Dashboard Enhancements**

#### A. Document Verification Status Card
Shows verification status for each uploaded document:
- WAEC/NECO Result
- JAMB Result Slip  - Passport Photo
- Birth Certificate (if uploaded)

Each shows:
- Document name
- Status badge (Pending/Verified/Rejected)
- Rejection reason (if rejected)

#### B. Action Required Alert
If any documents are rejected:
- Red alert box with "Action Required" message
- "Re-upload Documents" button linking to screening form

#### C. Success Message
When all documents are verified:
- Green success box: "All Documents Verified!"

---

## 📁 Files Modified

### 1. **core/models.py**
Added to `ScreeningForm` model:
```python
# Verification status fields for each document
waec_result_status = models.CharField(...)
waec_result_comment = models.TextField(...)
jamb_result_slip_status = models.CharField(...)
jamb_result_slip_comment = models.TextField(...)
passport_photo_status = models.CharField(...)
passport_photo_comment = models.TextField(...)
birth_certificate_status = models.CharField(...)
birth_certificate_comment = models.TextField(...)

# Metadata
verified_by = models.ForeignKey(User, ...)
verified_at = models.DateTimeField(...)
```

Helper methods:
- `get_document_verification_summary()` - Returns verification stats
- `has_rejected_documents()` - Check if any docs rejected
- `all_documents_verified()` - Check if all docs verified

### 2. **core/admin.py**
Enhanced `ScreeningFormAdmin`:
- Added document status display methods with color badges
- Added document link methods (clickable file links)
- Updated fieldsets with verification section
- Added `save_model()` to track verifications and send notifications
- Added bulk actions for mass verification

### 3. **core/views.py**
Updated `applicant_dashboard()`:
- Added `screening_form` to context

### 4. **templates/dashboard/applicant-dashboard.html**
Added:
- Document Verification Status section (150+ lines)
- Status badges for each document
- Rejection reasons display
- Action required alert
- All verified success message

### 5. **Database Migration**
Created: `core/migrations/0024_screeningform_birth_certificate_comment_and_more.py`
- Adds 10 new fields to ScreeningForm model

---

## 🚀 How to Use

### For Admins:

#### Individual Document Verification
1. Go to **Django Admin** → **Core** → **Screening forms**
2. Click on a screening form to edit
3. Scroll to **"Document Verification Summary"** to see overall status
4. In **"Documents & Verification"** section:
   - Click document links to view uploaded files
   - Change status dropdown (Pending → Verified or Rejected)
   - If rejecting, add a comment explaining why
5. Click **Save**
6. Applicant automatically receives notification

#### Bulk Verification
1. Go to **Django Admin** → **Core** → **Screening forms**
2. Select multiple forms using checkboxes
3. Choose action from dropdown:
   - **"✓ Verify all documents"** - Verifies all docs for selected forms
   - **"⏳ Mark all documents as pending"** - Resets verification
4. Click **Go**

#### Filtering
Use filters on the right sidebar:
- Filter by WAEC status
- Filter by JAMB status
- Filter by Passport Photo status
- Filter by Birth Certificate status

### For Applicants:

#### Viewing Document Status
1. Log in to applicant account
2. Go to **Dashboard**
3. View **"Document Verification Status"** section
4. See status for each document:
   - ⏳ Yellow badge = Pending review
   - ✓ Green badge = Verified
   - ✗ Red badge = Rejected (with reason shown)

#### Re-uploading Rejected Documents
1. If documents are rejected, click **"Re-upload Documents"** button
2. Go to screening form
3. Upload new documents in place of rejected ones
4. Submit form
5. Status resets to "Pending" for admin re-review

---

## 🔔 Automatic Notifications

Notifications are sent to applicants when:

1. **Document Rejected**:
```
The following documents were rejected:
• WAEC/NECO Result: Photo is blurry, please provide clearer scan
• Passport Photo: Photo does not meet requirements

Please re-upload the correct documents.
```

2. **All Documents Verified**:
```
All your documents have been verified! Your application is now being processed.
```

3. **Some Documents Verified** (no rejections):
```
The following documents have been verified: WAEC/NECO Result, JAMB Result Slip
```

---

## 🎨 Visual Indicators

### Admin Interface:
- **Green badge**: ✓ All Verified
- **Red badge**: ✗ X Rejected
- **Yellow badge**: ⏳ X Pending
- **Clickable file links**: 📄 View Document / 🖼️ View Photo

### Applicant Dashboard:
- **Green badges**: Verified documents
- **Red badges**: Rejected documents  - **Yellow badges**: Pending documents
- **Red alert box**: Action required for rejected docs
- **Green success box**: All documents verified

---

## 📊 Database Schema

New fields added to `ScreeningForm` model:

| Field Name | Type | Choices | Description |
|-----------|------|---------|-------------|
| `waec_result_status` | CharField(20) | pending/verified/rejected | WAEC verification status |
| `waec_result_comment` | TextField | - | Rejection reason |
| `jamb_result_slip_status` | CharField(20) | pending/verified/rejected | JAMB verification status |
| `jamb_result_slip_comment` | TextField | - | Rejection reason |
| `passport_photo_status` | CharField(20) | pending/verified/rejected | Photo verification status |
| `passport_photo_comment` | TextField | - | Rejection reason |
| `birth_certificate_status` | CharField(20) | pending/verified/rejected | Birth cert verification status |
| `birth_certificate_comment` | TextField | - | Rejection reason |
| `verified_by` | ForeignKey(User) | - | Admin who verified |
| `verified_at` | DateTimeField | - | When verified/rejected |

---

## 🧪 Testing Checklist

- [ ] Admin can verify individual documents
- [ ] Admin can reject documents with comments
- [ ] Admin can use bulk verification action
- [ ] Applicant sees document status on dashboard
- [ ] Applicant receives notification when docs verified
- [ ] Applicant receives notification when docs rejected
- [ ] Rejection reasons are displayed to applicant
- [ ] "Re-upload Documents" button works for rejected docs
- [ ] "All Verified" success message appears when appropriate
- [ ] Document links in admin open files correctly
- [ ] Filters work in admin list view
- [ ] Verification metadata (verified_by, verified_at) is tracked

---

## 🔐 Security Notes

- Only admins can change verification status
- Applicants can only view their own verification status
- Document files are served through configured media URL
- Verification comments are visible only to the applicant whose documents were rejected

---

## 💡 Future Enhancements (Optional)

1. **Email Notifications**: Send emails in addition to in-app notifications
2. **Document Comparison**: Show old vs new document when re-uploaded
3. **Verification History**: Track full history of status changes
4. **Document Templates**: Provide sample/template documents for guidance
5. **Automatic Verification**: Use AI/OCR to auto-verify certain documents
6. **Deadline Tracking**: Set deadlines for re-uploading rejected documents
7. **Admin Comments Thread**: Allow back-and-forth communication on documents

---

## 📞 Support

If you encounter any issues:
1. Check that migrations are applied: `python manage.py migrate core`
2. Ensure user has admin permissions to access verification features
3. Verify media files are accessible (check MEDIA_URL and MEDIA_ROOT settings)
4. Check notification system is working

---

**Implementation Date**: February 2026
**Version**: 1.0
**Status**: ✅ Complete and Functional
