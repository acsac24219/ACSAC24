import org.json4s._
import org.json4s.JsonDSL._
import org.json4s.native.JsonMethods._
import io.joern.joerncli.JoernVectors.formats
import scala.collection.mutable.ListBuffer
import java.time.Instant

// Main execution function
@main def exec(cpgFile: String, outFile: String) = {
   importCpg(cpgFile)

   // Extracting file names from the given path and parsing JSON
   val startTime1 = Instant.now().toEpochMilli()
   val file_list = cpg.file.name("src/.*/.*.cpp")
   val json: JValue = parse(file_list.toJson)
   val endTime1 = Instant.now().toEpochMilli()
   val executionTime1 = endTime1 - startTime1

   // Buffers to store JSON objects
   val all_json_objects_methods_list_split = ListBuffer[JValue]()
   val last_json_objects_rpc_call_list_split = ListBuffer[JValue]()

   // Processing each file's method list and building all_json_objects_methods_list_split
   val startTime2 = Instant.now().toEpochMilli()
   for (item <- json.children) {
       val cpg_file_id = (item \ "id").extract[Int]
       val cpg_file_name = (item \ "name").extract[String]
       val cpg_file_name_split = cpg_file_name.split("/")(1)
       
       val methods_list = cpg.file.id(cpg_file_id).method.fullName.dedup
       val methods_list_split = methods_list
                                    .filter(item => item.startsWith("social_network") || item.startsWith("media_service") || item.startsWith("OnReceivedWorker"))
                                    .filterNot(s => s.contains("~") || s.contains("<lambda>") || s.contains("operator") || s.contains("Rabbitmq") || s.contains("Redis"))
                                    .map(_.split("\\."))
                                    .filter(item => item.length == 3 || item.headOption.contains("OnReceivedWorker"))
                                    .filterNot(_.lastOption.exists(_.contains("_")))
                                    .collect {
                                        case Array(applicationName, serviceName, rpcFuncName, _*) =>
                                          ("application_name" -> applicationName) ~
                                          ("service_name" -> serviceName) ~
                                          ("rpc_func_name" -> rpcFuncName) ~
                                          ("cpg_file_id" -> cpg_file_id) ~
                                          ("cpg_file_name" -> cpg_file_name) ~
                                          ("cpg_file_name_split" -> cpg_file_name_split)
                                        case Array(firstElement: String) =>
                                          ("application_name" -> "social_network") ~
                                          ("service_name" -> "WriteHomeTimelineService") ~
                                          ("rpc_func_name" -> firstElement) ~
                                          ("cpg_file_id" -> cpg_file_id) ~
                                          ("cpg_file_name" -> cpg_file_name) ~
                                          ("cpg_file_name_split" -> cpg_file_name_split)
                                    }
                                    .map(Extraction.decompose(_))

       all_json_objects_methods_list_split ++= methods_list_split
   }
   val endTime2 = Instant.now().toEpochMilli()
   val executionTime2 = endTime2 - startTime2

   // Processing RPC calls and building last_json_objects_rpc_call_list_split
   val startTime3 = Instant.now().toEpochMilli()
   val serviceExecutionTimes = scala.collection.mutable.Map[String, Long]().withDefaultValue(0)

   for (x <- all_json_objects_methods_list_split.children) {
       val cpg_file_id = (x \ "cpg_file_id").extract[Int]
       val cpg_file_name = (x \ "cpg_file_name").extract[String]
       val service_name = (x \ "service_name").extract[String]
       val cpg_file_name_split_ext = (x \ "cpg_file_name_split").extract[String]

       for (y <- all_json_objects_methods_list_split.children) {
           val rpc_func_name = (y \ "rpc_func_name").extract[String]
           val call_service_name = (y \ "service_name").extract[String]
           val cpg_file_name_split = (y \ "cpg_file_name_split").extract[String]

           val startTimeCall = Instant.now().toEpochMilli() // Record start time of each call
           val last_call_method = cpg.call.name(rpc_func_name).location.filter(_.filename == cpg_file_name).toJson
           if (last_call_method.trim.nonEmpty && last_call_method != "[]") {
               parse(last_call_method) match {
                 case JArray(items) =>
                     items.foreach {
                       case obj: JObject =>
                         val updatedObj = obj ~ ("current_service_handler" -> service_name) ~ 
                                              ("current_service_name" -> cpg_file_name_split_ext) ~
                                              ("rpc_func_name" -> rpc_func_name) ~ 
                                              ("call_service_handler" -> call_service_name) ~
                                              ("call_service_name" -> cpg_file_name_split)
                         val symbolValue = updatedObj.values.getOrElse("symbol", "").asInstanceOf[String]
                         val newValue = symbolValue.replaceAll("[\\n\\s]", "")
                         val methodFullName = updatedObj.values.getOrElse("methodFullName", "").asInstanceOf[String]
                         val updatedJson = updatedObj ~ ("current_service_method_full_name", methodFullName) ~
                                            ("rpc_func_name_symbol", newValue)
                         last_json_objects_rpc_call_list_split += updatedJson
                         val endTimeCall = Instant.now().toEpochMilli() // Record end time of each call
                         val executionTimeCall = endTimeCall - startTimeCall // Calculate call execution time
                         println(s"Call: $rpc_func_name - Execution Time: $executionTimeCall ms")
                         // Add execution time to the corresponding service
                         serviceExecutionTimes(service_name) += executionTimeCall
                       case _ =>
                         println("Item is not a JSON object")
                     }
                 case _ =>
                   println("Not a JSON array")
               }
           }
       }
   }

   // Print execution times per service
   println("Execution Times per Service:")
   serviceExecutionTimes.foreach { case (service, time) =>
       println(s"Service: $service - Total Execution Time: $time ms")
   }

   val endTime3 = Instant.now().toEpochMilli()
   val executionTime3 = endTime3 - startTime3

   // Writing output to file
   val startTime4 = Instant.now().toEpochMilli()
   pretty(render(last_json_objects_rpc_call_list_split)) #>> outFile
   val endTime4 = Instant.now().toEpochMilli()
   val executionTime4 = endTime4 - startTime4

   // Print execution times
   println("Execution Times:")
   println(s"Extracting file names and parsing JSON: $executionTime1 ms")
   println(s"Processing method lists and building all_json_objects_methods_list_split: $executionTime2 ms")
   println(s"Processing RPC calls and building last_json_objects_rpc_call_list_split: $executionTime3 ms")
   println(s"Writing output to file: $executionTime4 ms")
   println(s"Total execution time: ${executionTime1 + executionTime2 + executionTime3 + executionTime4} ms")
}
