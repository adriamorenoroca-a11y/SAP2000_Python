import comtypes
import comtypes.client


def conectar_sap():
    """Conecta con SAP2000 y devuelve el SapModel."""
    helper    = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper    = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    SapObject.ApplicationStart()
    SapModel  = SapObject.SapModel
    SapModel.InitializeNewModel()
    SapModel.File.NewBlank()
    SapModel.SetPresentUnits(6)  # kN, m, C
    return SapModel
