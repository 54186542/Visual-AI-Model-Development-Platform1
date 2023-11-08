import json
import importlib
from fastapi import APIRouter
from fastapi import Body

router = APIRouter()


@router.post("/trainModel")
async def trainModel(data=Body(None)):
    print(data)
    json_string = json.dumps(data)
    # 模拟读取JSON字符串
    # json_string = '''
    # {
    #     "task":"ImageClassification",
    #     "import_data":{
    #     "file_type":"import_zip_data",
    #     "file_path":"handwriting_digits.zip"
    #     },
    #     "data_preprocessing":[
    #         {
    #             "name":"normalize_images",
    #             "arguments":{
    #                 "mean":""
    #             }
    #         },
    #         {
    #             "name":"standardize_images",
    #             "arguments":{
    #                 "mean":""
    #             }
    #         }
    #     ],
    #     "model_selection":{
    #         "name":"CNN",
    #         "arguments":{
    #             "epochs":"",
    #         "layer":{
    #         "conv2d1": [16, 2],
    #         "ReLU1": -1,
    #         "maxpool2d": 2,
    #         "conv2d2": [32, 2],
    #         "ReLU2": -1,
    #         "linear1": 10
    #     }
    #         }
    #     }
    # }'''

    # ① 读取JSON，存储在data_dict中
    data_dict = json.loads(json_string)

    # ② 确定任务类型
    task = data_dict["task"]  # 由于列表中只有一个值，直接取出来
    file_path = data_dict["import_data"]["file_path"]  # 读取路径参数

    # 根据任务类型选择对应的目录
    module_path = task

    # ③ 读取"import_data"函数名称
    import_function_name = data_dict["import_data"]["file_type"]  # 由于列表中只有一个值，直接取出来
    import_module = importlib.import_module(f"{module_path}.import_data")
    import_function = getattr(import_module, import_function_name)

    # 使用别名读取数据
    data = import_function(file_path)

    # ④ 数据预处理
    for preprocessing_step in data_dict["data_preprocessing"]:
        # 获取函数名称和参数
        function_name = preprocessing_step["name"]
        function_arguments = preprocessing_step["arguments"]

        # 清洗参数字典
        cleaned_arguments = {k: v for k, v in function_arguments.items() if v != '' and v is not None}

        # 添加data到参数字典中
        cleaned_arguments['data'] = data

        # 调用函数
        preprocessing_module = importlib.import_module(f"{module_path}.data_preprocessing")
        preprocessing_function = getattr(preprocessing_module, function_name)
        data = preprocessing_function(**cleaned_arguments)

    # ⑤ 模型选择和训练
    model_name, model_arguments = data_dict["model_selection"]["name"], data_dict["model_selection"]["arguments"]
    cleaned_model_arguments = {k: v for k, v in model_arguments.items() if v != '' and v is not None and v != -1}
    cleaned_model_arguments['data'] = data

    # 调用模型选择模块中的模型函数
    model_module = importlib.import_module(f"{module_path}.model_selection")
    model_function = getattr(model_module, model_name)
    model = model_function(**cleaned_model_arguments)

    # 模型评估还没写

    # 这里是传回给java的东西。
    return {"result": data}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("yuuki_reload_execution:router", host="127.0.0.1", port=8000)