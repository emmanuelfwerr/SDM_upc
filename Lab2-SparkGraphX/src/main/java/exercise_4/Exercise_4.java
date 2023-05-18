package exercise_4;

import com.clearspring.analytics.util.Lists;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SQLContext;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.MetadataBuilder;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;
import org.graphframes.GraphFrame;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class Exercise_4 {

	static final double DAMPING_FACTOR = 0.85; // --> vertex teleport probability = 0.15
	static final int MAX_ITERATIONS = 20;
	
	public static void wikipedia(JavaSparkContext ctx, SQLContext sqlCtx) throws Exception {
		// Loading vertices
		java.util.List<Row> vertices_list = new ArrayList<Row>();
		File file_vertices = new File("src/main/resources/wiki-vertices.txt");

		BufferedReader vertex_br = new BufferedReader(new FileReader(file_vertices));
			String vertex;
			while ((vertex = vertex_br.readLine()) != null) {
				String[] vertices = vertex.split("\t");
				Row rowVertex = RowFactory.create(Long.parseLong(vertices[0]), vertices[1]);
				vertices_list.add(rowVertex);
			}

		JavaRDD<Row> vertices_rdd = ctx.parallelize(vertices_list, 15);

		StructType vertices_schema = new StructType(new StructField[]{
				new StructField("id", DataTypes.LongType, false, new MetadataBuilder().build()),
				new StructField("title", DataTypes.StringType, false, new MetadataBuilder().build())
		});
		Dataset<Row> vertices =  sqlCtx.createDataFrame(vertices_rdd, vertices_schema);


		// Creating Edges
		java.util.List<Row> edges_list = new ArrayList<Row>();
		File file_edges = new File("src/main/resources/wiki-edges.txt");

		BufferedReader edge_br = new BufferedReader(new FileReader(file_edges));
			String relation;
			while ((relation = edge_br.readLine()) != null) {
				String[] edges = relation.split("\t");
				Row rowEdge = RowFactory.create(Long.parseLong(edges[0]), Long.parseLong(edges[1]));
				edges_list.add(rowEdge);
			}

		JavaRDD<Row> edges_rdd = ctx.parallelize(edges_list, 15);

		StructType edges_schema = new StructType(new StructField[]{
				new StructField("src", DataTypes.LongType, false, new MetadataBuilder().build()),
				new StructField("dst", DataTypes.LongType, false, new MetadataBuilder().build())
		});
		Dataset<Row> edges =  sqlCtx.createDataFrame(edges_rdd, edges_schema);

		GraphFrame gf = GraphFrame.apply(vertices, edges);

		// Computing PageRank
		gf.pageRank().maxIter(MAX_ITERATIONS).resetProbability(1-DAMPING_FACTOR).run().vertices().select("id", "title", "pagerank").orderBy(org.apache.spark.sql.functions.col("pagerank").desc()).show(10);


	}
	
}
