from spire.doc import *
from spire.doc.common import *



# Create an object of the Document class
doc = Document()
# Load a Word document
doc.LoadFromFile("InsertOLE.docx")

i = 1 
# Iterate through all sections of the Word document
for k in range(doc.Sections.Count):
    sec = doc.Sections.get_Item(k)
    # Iterate through all child objects in the body of each section
    for j in range(sec.Body.ChildObjects.Count):
        obj = sec.Body.ChildObjects.get_Item(j)
        # Check if the child object is a paragraph
        if isinstance(obj, Paragraph):
            par = obj if isinstance(obj, Paragraph) else None
            # Iterate through the child objects in the paragraph
            for m in range(par.ChildObjects.Count):
                o = par.ChildObjects.get_Item(m)
                # Check if the child object is an OLE object
                if o.DocumentObjectType == DocumentObjectType.OleObject:
                    ole = o if isinstance(o, DocOleObject) else None
                    s = ole.ObjectType
                    # Check if the OLE object is a PDF file
                    if s.startswith("AcroExch.Document"):
                        ext = ".pdf"
                    # Check if the OLE object is an Excel spreadsheet
                    elif s.startswith("Excel.Sheet"):
                        ext = ".xlsx"
                    # Check if the OLE object is a PowerPoint presentation
                    elif s.startswith("PowerPoint.Show"):
                        ext = ".pptx"
                    else:
                        continue
                    # Write the data of OLE into a file in its native format
                    with open(f"Output/OLE{i}{ext}", "wb") as file:
                            file.write(ole.NativeData)                        
                    i += 1

doc.Close()
