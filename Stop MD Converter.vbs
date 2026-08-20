' Stop MD Converter - Double-click to shut down the running server

Dim http
Set http = CreateObject("WinHttp.WinHttpRequest.5.1")

On Error Resume Next
http.Open "POST", "http://localhost:5000/api/shutdown", False
http.Send
On Error GoTo 0

If http.Status = 200 Or http.Status = 0 Then
    MsgBox "MD Converter stopped.", vbInformation, "MD Converter"
Else
    MsgBox "MD Converter does not appear to be running.", vbExclamation, "MD Converter"
End If
