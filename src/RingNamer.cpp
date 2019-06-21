// RingNamer.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <string>
#include <iostream>
#include <experimental/filesystem>
#include <vector>
#include <omp.h>
#include <chrono>

#include <TopoDS_Shape.hxx>
#include <IGESControl_Reader.hxx>
#include <BRepMesh_IncrementalMesh.hxx>
#include <TopLoc_Location.hxx>
#include <Poly_Triangulation.hxx>
#include <TopExp_Explorer.hxx>
#include <Poly_Array1OfTriangle.hxx>
#include <Bnd_Box.hxx>
#include <BRepBndLib.hxx>
#include <BRep_Builder.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include <IGESControl_Writer.hxx>

#include <IVtkOCC_Shape.hxx>
#include <IVtkTools_ShapeDataSource.hxx>
#include <AIS_InteractiveContext.hxx>
#include <V3d_View.hxx>
#include <AIS_Shape.hxx>

#include <vtkSmartPointer.h>
#include <vtkLineSource.h>
#include <vtkProperty.h>
#include <vtkPolyDataMapper.h>
#include <vtkPolyData.h>
#include <vtkActor.h>
#include <vtkRenderWindow.h>
#include <vtkRenderer.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkAxesActor.h>
#include <vtkOrientationMarkerWidget.h>
#include "vtkAutoInit.h"

// #include "vtkOCCReader.h"

VTK_MODULE_INIT(vtkRenderingOpenGL2);
VTK_MODULE_INIT(vtkInteractionStyle);
VTK_MODULE_INIT(vtkRenderingFreeType);


gp_Vec GetCenter(TopoDS_Shape& shape)
{
	Bnd_Box box;
	BRepBndLib::Add(shape, box);
	Standard_Real xMin, yMin, zMin, xMax, yMax, zMax;
	box.Get(xMin, yMin, zMin, xMax, yMax, zMax);
	Standard_Real dx = xMax - xMin;
	Standard_Real dy = yMax - yMin;
	Standard_Real dz = zMax - zMin;
	std::cout << dx << "\t" << dy << "\t" << dz << std::endl;
	Standard_Real center[3] = { xMin + dx * 0.5, yMin + dy * 0.5, zMin + dz * 0.5 };
	std::cout << center[0] << "\t" << center[1] << "\t" << center[2] << std::endl;

	gp_Vec aVec;
	aVec.SetCoord(center[0], center[1], center[2]);
	return aVec;
}

Standard_Real GetDY(TopoDS_Shape& shape)
{
	Bnd_Box box;
	BRepBndLib::Add(shape, box);
	Standard_Real xMin, yMin, zMin, xMax, yMax, zMax;
	box.Get(xMin, yMin, zMin, xMax, yMax, zMax);
	Standard_Real dy = yMax - yMin;

	return dy;
}

void WriteFile(TopoDS_Shape& shape, const char* filePath)
{
	IGESControl_Writer writer;
	writer.AddShape(shape);
	writer.Write(filePath);
}

void RenderPolyData(vtkSmartPointer<vtkPolyData> pData)
{
	//Usual vtk pipeline to display required shape
	vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
	vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
	mapper->SetInputData(pData);
	vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
	actor->SetMapper(mapper);
	renderer->AddActor(actor);
	renderer->SetBackground(0.1, 0.2, 0.3);

	vtkSmartPointer<vtkRenderWindow> window = vtkSmartPointer<vtkRenderWindow>::New();
	window->AddRenderer(renderer);
	vtkSmartPointer<vtkRenderWindowInteractor> interactor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
	interactor->SetRenderWindow(window);
	window->Render();
	
	vtkSmartPointer<vtkInteractorStyleTrackballCamera> style = vtkSmartPointer<vtkInteractorStyleTrackballCamera>::New(); //like paraview
	interactor->SetInteractorStyle(style);
	interactor->Start();
}

// vtkSmartPointer<vtkPolyData> ReadOCCFile(const char* filePath)
// {
// 	vtkSmartPointer<vtkOCCReader> pOccReader = vtkSmartPointer<vtkOCCReader>::New();
// 	pOccReader->SetFileName(filePath);
// 	pOccReader->Update();
	
// 	//Usual vtk pipeline to display required shape
// 	vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
// 	vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
// 	mapper->SetInputConnection(pOccReader->GetOutputPort());
// 	vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
// 	actor->SetMapper(mapper);
// 	renderer->AddActor(actor);
// 	renderer->SetBackground(0.1, 0.2, 0.3);

// 	vtkSmartPointer<vtkRenderWindow> window = vtkSmartPointer<vtkRenderWindow>::New();
// 	window->AddRenderer(renderer);
// 	vtkSmartPointer<vtkRenderWindowInteractor> interactor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
// 	interactor->SetRenderWindow(window);
// 	window->Render();
	
// 	vtkSmartPointer<vtkInteractorStyleTrackballCamera> style = vtkSmartPointer<vtkInteractorStyleTrackballCamera>::New(); //like paraview
// 	interactor->SetInteractorStyle(style);
// 	interactor->Start();

// 	vtkSmartPointer<vtkPolyData> pPolyData;
// 	return pPolyData;
// }

void ReadDispFile(const char* filePath)
{
	IGESControl_Reader Reader;
	int status = Reader.ReadFile(filePath);
	if (status != IFSelect_RetDone)
	{
		return;
	}

	Reader.TransferRoots();
	TopoDS_Shape tdsshape = Reader.OneShape();

	//Converting OpenCascade shape to vtk shape to render it in vtk window
	IVtkOCC_Shape::Handle aShapeImpl = new IVtkOCC_Shape(tdsshape);
	vtkSmartPointer<IVtkTools_ShapeDataSource> pDataSource = vtkSmartPointer<IVtkTools_ShapeDataSource>::New();
	pDataSource->SetShape(aShapeImpl);
	pDataSource->Update();

	RenderPolyData(pDataSource->GetOutput());
}

TopoDS_Shape ReadFile(const char* filePath)
{
	IGESControl_Reader Reader;
	int status = Reader.ReadFile(filePath);
	TopoDS_Shape tdsshape;
	if (status == IFSelect_RetDone)
	{
		Reader.TransferRoots();
		tdsshape = Reader.OneShape();
	}
	return tdsshape;
}

void PrepareFonts()
{
	std::string path = "E://projects//current//Ryan_Ring//IGES//Fonts//Fonts_local//";
	std::string newPath = "E://projects//current//Ryan_Ring//IGES//Fonts//Fonts//";
	std::string files[] = { "A.iges","B.iges","C.iges","D.iges" ,"E.iges" ,"F.iges" ,"G.iges" ,"H.iges" ,"I.iges" ,"G.iges" ,"H.iges" ,"J.iges" ,"K.iges" ,"L.iges" ,"M.iges" ,"N.iges" ,"O.iges" ,"P.iges" ,"Q.iges" ,"R.iges" ,"S.iges" ,"T.iges","U.iges","V.iges","W.iges","X.iges","Y.iges","Z.iges" };
	for (int i = 0; i < 28; i++)
	{
		std::string aFile = path + files[i];
		std::cout << "File ... " << aFile << std::endl;
		TopoDS_Shape aShape = ReadFile(aFile.c_str());

		gp_Trsf aTrans;
		gp_Vec aVec = GetCenter(aShape);
		aVec.Multiply(-1);
		aTrans.SetTranslation(aVec);
		BRepBuilderAPI_Transform aBRepTrsf(aShape, aTrans);
		TopoDS_Shape trShape = aBRepTrsf.Shape();

		gp_Trsf aRot;
		aRot.SetRotation(gp::OX(), 1.5708);
		BRepBuilderAPI_Transform bBRepTrsf(trShape, aRot);
		trShape = bBRepTrsf.Shape();
		GetCenter(trShape);

		gp_Trsf bRot;
		bRot.SetRotation(gp::OZ(), 1.5708);
		BRepBuilderAPI_Transform cBRepTrsf(trShape, bRot);
		trShape = cBRepTrsf.Shape();
		GetCenter(trShape);

		std::string newFile = newPath + files[i];
		std::cout << "File ... " << newFile << std::endl;
		WriteFile(trShape, newFile.c_str());
	}
}

double ComputeRotAngle(double prevAngle, TopoDS_Shape& prevShape, TopoDS_Shape& currShape)
{
	Standard_Real prevDY = GetDY(prevShape);
	Standard_Real currentDY = GetDY(currShape);

	return 0.0;
}

void Render(std::vector<vtkPolyData*>& polyDatas)
{
	//Usual vtk pipeline to display required shape
	vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
	for (auto it : polyDatas)
	{
		vtkSmartPointer<vtkPolyDataMapper> mapper = vtkSmartPointer<vtkPolyDataMapper>::New();
		mapper->SetInputData(it);
		vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
		actor->SetMapper(mapper);
		renderer->AddActor(actor);
	}
	renderer->SetBackground(0.1, 0.2, 0.3);

	vtkSmartPointer<vtkRenderWindow> window = vtkSmartPointer<vtkRenderWindow>::New();
	window->AddRenderer(renderer);
	vtkSmartPointer<vtkRenderWindowInteractor> interactor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
	interactor->SetRenderWindow(window);
	window->Render();

	// Axes
	vtkSmartPointer<vtkAxesActor> axes = vtkSmartPointer<vtkAxesActor>::New();
	vtkSmartPointer<vtkOrientationMarkerWidget> widget = vtkSmartPointer<vtkOrientationMarkerWidget>::New();
	widget->SetOutlineColor(0.9300, 0.5700, 0.1300);
	widget->SetOrientationMarker(axes);
	widget->SetInteractor(interactor);
	widget->SetViewport(0.0, 0.0, 0.4, 0.4);
	widget->SetEnabled(1);
	widget->InteractiveOn();

	// Origin
	vtkSmartPointer<vtkLineSource> xLS = vtkSmartPointer<vtkLineSource>::New();
	xLS->SetPoint1(0.0, 0.0, 0.0);
	xLS->SetPoint2(10.0, 0.0, 0.0);
	xLS->Update();
	vtkSmartPointer<vtkPolyDataMapper> xLSmapper = vtkSmartPointer<vtkPolyDataMapper>::New();
	xLSmapper->SetInputData(xLS->GetOutput());
	vtkSmartPointer<vtkActor> xLSactor = vtkSmartPointer<vtkActor>::New();
	xLSactor->SetMapper(xLSmapper);
	xLSactor->GetProperty()->SetColor(1.0, 0.0, 0.0);
	renderer->AddActor(xLSactor);

	vtkSmartPointer<vtkLineSource> yLS = vtkSmartPointer<vtkLineSource>::New();
	yLS->SetPoint1(0.0, 0.0, 0.0);
	yLS->SetPoint2(0.0, 10.0, 0.0);
	yLS->Update();
	vtkSmartPointer<vtkPolyDataMapper> yLSmapper = vtkSmartPointer<vtkPolyDataMapper>::New();
	yLSmapper->SetInputData(yLS->GetOutput());
	vtkSmartPointer<vtkActor> yLSactor = vtkSmartPointer<vtkActor>::New();
	yLSactor->SetMapper(yLSmapper);
	yLSactor->GetProperty()->SetColor(0.0, 1.0, 0.0);
	renderer->AddActor(yLSactor);

	vtkSmartPointer<vtkLineSource> zLS = vtkSmartPointer<vtkLineSource>::New();
	zLS->SetPoint1(0.0, 0.0, 0.0);
	zLS->SetPoint2(0.0, 0.0, 10.0);
	zLS->Update();
	vtkSmartPointer<vtkPolyDataMapper> zLSmapper = vtkSmartPointer<vtkPolyDataMapper>::New();
	zLSmapper->SetInputData(zLS->GetOutput());
	vtkSmartPointer<vtkActor> zLSactor = vtkSmartPointer<vtkActor>::New();
	zLSactor->SetMapper(zLSmapper);
	zLSactor->GetProperty()->SetColor(0.0, 0.0, 1.0);
	renderer->AddActor(zLSactor);

	renderer->Render();
	vtkSmartPointer<vtkInteractorStyleTrackballCamera> style = vtkSmartPointer<vtkInteractorStyleTrackballCamera>::New(); //like paraview
	interactor->SetInteractorStyle(style);
	interactor->Start();
}

void TranslateShape(TopoDS_Shape& aShape, gp_Vec aVec)
{
	gp_Trsf aTrans;
	aTrans.SetTranslation(aVec);
	BRepBuilderAPI_Transform aBRepTrsf(aShape, aTrans);
	aShape = aBRepTrsf.Shape();
}

void RotateShape(TopoDS_Shape& aShape, const gp_Ax1& axis, const double& theta)
{
	gp_Trsf aRot;
	aRot.SetRotation(axis, theta);
	BRepBuilderAPI_Transform aBRepTrsf(aShape, aRot);
	aShape = aBRepTrsf.Shape();
}

void TransferToLocalCoords(TopoDS_Shape& aShape)
{
	gp_Trsf aTrans;
	gp_Vec aVec = GetCenter(aShape);
	aVec.Multiply(-1);
	aTrans.SetTranslation(aVec);
	BRepBuilderAPI_Transform aBRepTrsf(aShape, aTrans);
	aShape = aBRepTrsf.Shape();
}

//Assumption : Shapes are in local coords
std::vector<double> CalculateTheta(std::vector<TopoDS_Shape>& shapes, double radius)
{
	std::vector<double> thetas;
	for (auto it : shapes)
	{
		TranslateShape(it, gp_Vec(radius, 0, 0));
		double Dy = GetDY(it);
		gp_Vec aVec(radius, Dy*0.5, 0.0);
		gp_Vec xAxis(1, 0, 0);
		double theta = xAxis.Angle(aVec);
		thetas.push_back(theta);
	}
	return thetas;
}

std::vector<TopoDS_Shape> PlaceCharacters(std::string chars, double radius, double& finalAngle)
{
	std::string charsPath = "./Fonts/";
	
	std::vector<char> stringChars(chars.begin(), chars.end());
	int sizeChars = stringChars.size();
	std::vector<TopoDS_Shape> charShapes(sizeChars);

	#pragma omp parallel for 
	for (int i =0; i< sizeChars; i++)
	{
		std::cout<<"To Read File : "<<stringChars[i]<<std::endl;
		std::string charFilePath = charsPath + stringChars[i] + ".iges";
		std::cout<<"Read File : "<<charFilePath<<std::endl;
		TopoDS_Shape charShape = ReadFile(charFilePath.c_str());
		charShapes[i] = charShape;
	}

	// Find thetas
	std::vector<double> thetas = CalculateTheta(charShapes, radius);

	double currTheta = 0;
	for (int i = 0; i < charShapes.size(); i++)
	{
		if (i)
		{
			currTheta += thetas[i - 1] + thetas[i];
		}
		else
		{
			currTheta += thetas[i];
		}
		TranslateShape(charShapes[i], gp_Vec(radius, 0, 0));
		RotateShape(charShapes[i], gp::OZ(), currTheta);
	}
	finalAngle = currTheta + thetas.back();

	return charShapes;
}

std::vector<TopoDS_Shape> PlaceDesigns(TopoDS_Shape& design, double radius, const double& startAngle)
{
	//Predict number of designs can be placed
	std::vector<TopoDS_Shape> shapes;
	TopoDS_Shape aDesign = design;
	shapes.push_back(aDesign);
	std::vector<double> thetas = CalculateTheta(shapes, radius);
	double avilableTheta = 6.2832 - startAngle;
	int nDesigns = avilableTheta / (thetas[0]*2.0);
	double theta = (avilableTheta / nDesigns)*0.5;

	shapes.resize(nDesigns);
	std::fill(shapes.begin(), shapes.end(), aDesign);
	thetas.resize(nDesigns);
	std::fill(thetas.begin(), thetas.end(), theta);

	double currTheta = startAngle;
	for (int i = 0; i < nDesigns; i++)
	{
		if (i)
		{
			currTheta += thetas[i-1]+thetas[i];
		}
		else
		{
			currTheta += thetas[i];
		}
		// TODO : translate before this
		TranslateShape(shapes[i], gp_Vec(radius, 0, 0));
		RotateShape(shapes[i], gp::OZ(), currTheta);
	}

	return shapes;
}

// int main(int argc, char** argv)
// {
// 	#pragma omp parallel num_threads(3)
// 	{
// 		int id = omp_get_thread_num();
// 		int data = id;
// 		int total = omp_get_num_threads();
// 		printf("Greetings from process %d out of %d with Data %d\n", id, total, data);
// 	}
// 	printf("parallel for ends.\n");
// }

int main(int argc, char** argv)
{
	// Inputs would be ring type and characters
	if (argc != 2)
	{
		std::cout << "Invalid inputs";
		return 0;
	}

	Standard_CString ringType = argv[1];

	std::vector<vtkPolyData*> polys;

	TopoDS_Compound finalRing;
	TopoDS_Builder aBuider;
	aBuider.MakeCompound(finalRing);

	// Standard_CString ringPath = "E://projects//current//Ryan_Ring//IGES//A5//A5_rings_local.iges";
	std::string designPath = "./" + std::string(ringType) + "/A5_x_local.iges";
	std::string ringPath = "./" + std::string(ringType) + "/A5_body.iges";
	
	auto start = std::chrono::high_resolution_clock::now();
	TopoDS_Shape ringShape = ReadFile(ringPath.c_str());
	aBuider.Add(finalRing, ringShape);

	//Standard_CString designPath = "E://projects//current//Ryan_Ring//IGES//A5//A5_x_local.iges";
	TopoDS_Shape designShape = ReadFile(designPath.c_str());
	auto stop = std::chrono::high_resolution_clock::now();

	auto duration = std::chrono::duration_cast<std::chrono::microseconds>(stop - start); 
	std::cout<<"Read sucessfully in : "<< duration.count()*(1e-6) << std::endl; 

	//Converting OpenCascade shape to vtk shape to render it in vtk window
	IVtkOCC_Shape::Handle aShapeImpl = new IVtkOCC_Shape(ringShape);
	vtkSmartPointer<IVtkTools_ShapeDataSource> ringDS = vtkSmartPointer<IVtkTools_ShapeDataSource>::New();
	ringDS->SetShape(aShapeImpl);
	ringDS->Update();

	std::string name;
	bool finish = false;
	while (!finish)
	{
		polys.push_back(ringDS->GetOutput());
		name = "\0";
		std::cout<<"Type name"<<std::endl;
		std::cin >> name;
		std::cout<<"Creating Ring with name "<<name<<std::endl;

		double finalAngle = 0.0;
		std::vector<TopoDS_Shape> shapes = PlaceCharacters(name, 9.2, finalAngle);
		std::vector<TopoDS_Shape> designShapes = PlaceDesigns(designShape, 9.2, finalAngle);

		shapes.insert(shapes.end(), designShapes.begin(), designShapes.end());

		for (auto it : shapes)
		{
			aBuider.Add(finalRing, it);

			aShapeImpl = new IVtkOCC_Shape(it);
			vtkSmartPointer<IVtkTools_ShapeDataSource> designDS = vtkSmartPointer<IVtkTools_ShapeDataSource>::New();
			designDS->SetShape(aShapeImpl);
			designDS->Update();
			polys.push_back(designDS->GetOutput());

			// delete aShapeImpl;
			aShapeImpl = nullptr;
		}

		Render(polys);
		std::string outFile = std::string(ringType) + name + ".igs";
		WriteFile(finalRing, outFile.c_str());
		std::cout<<"Written to file "<<outFile<<std::endl;
		polys.clear();


		std::cout<<"Another Ring? \n Yes - 1 \n No - 0"<<endl;
		bool option;
		std::cin>>option;
		if(!option)
			finish = true;
	}

	std::cout << "Bimo!";
	std::getchar();
	return 0;
}
