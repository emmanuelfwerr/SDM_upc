package exercise_3;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import exercise_2.Exercise_2;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.graphx.*;
import org.apache.spark.storage.StorageLevel;
import scala.Tuple2;
import scala.collection.Iterator;
import scala.collection.JavaConverters;
import scala.reflect.ClassTag$;
import scala.runtime.AbstractFunction1;
import scala.runtime.AbstractFunction2;
import scala.runtime.AbstractFunction3;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Exercise_3 {

    private static class VProg extends AbstractFunction3<Long,Tuple2<Integer, List<Long>>,Tuple2<Integer, List<Long>>,Tuple2<Integer, List<Long>>> implements Serializable {
        @Override
        public Tuple2<Integer,List<Long>> apply( Long vertexID, Tuple2<Integer,List<Long>> vertexValue, Tuple2<Integer,List<Long>> message ) {
            if (vertexValue._1 <= message._1) {
                return vertexValue;
            } else {
                return message;
            }
        }
    }

    private static class sendMsg extends AbstractFunction1<EdgeTriplet<Tuple2<Integer, ArrayList<Long>>, Integer>, Iterator<Tuple2<Object, Tuple2<Integer, ArrayList<Long>>>>> implements Serializable {
        @Override
        public Iterator<Tuple2<Object, Tuple2<Integer, ArrayList<Long>>>> apply(EdgeTriplet<Tuple2<Integer, ArrayList<Long>>, Integer> triplet) {
            Tuple2<Object, Tuple2<Integer, ArrayList<Long>>> src_vertex = triplet.toTuple()._1(); // src vertex
            Tuple2<Object, Tuple2<Integer, ArrayList<Long>>> dst_vertex = triplet.toTuple()._2(); // dst vertex
            Integer edge_weight = triplet.toTuple()._3(); // edge weight

            ArrayList<Long> path = src_vertex._2._2;

            if (src_vertex._2._1 == Integer.MAX_VALUE || dst_vertex._2._1 - edge_weight <= src_vertex._2._1) {
                // do nothing
                return JavaConverters.asScalaIteratorConverter(new ArrayList<Tuple2<Object, Tuple2<Integer, ArrayList<Long>>>>().iterator()).asScala();
            } else {
                // propagate src_vertex value
                path.add(Long.parseLong(dst_vertex._1.toString()));
                return JavaConverters.asScalaIteratorConverter(Arrays.asList(new Tuple2<Object, Tuple2<Integer, ArrayList<Long>>>(triplet.dstId(), new Tuple2<Integer, ArrayList<Long>>(src_vertex._2._1 + edge_weight, path))).iterator()).asScala();
            }
        }
    }

    private static class merge extends AbstractFunction2<Tuple2<Integer, ArrayList<Long>>, Tuple2<Integer, ArrayList<Long>>, Tuple2<Integer, ArrayList<Long>>> implements Serializable {
        @Override
        public Tuple2<Integer, ArrayList<Long>> apply(Tuple2<Integer, ArrayList<Long>> o, Tuple2<Integer, ArrayList<Long>> o2) {
            if (o._1 <= o2._1) {
                return o;
            } else {
                return o2;
            }
        }
    }

    public static void shortestPathsExt(JavaSparkContext ctx) {
        Map<Long, String> labels = ImmutableMap.<Long, String>builder()
                .put(1l, "A")
                .put(2l, "B")
                .put(3l, "C")
                .put(4l, "D")
                .put(5l, "E")
                .put(6l, "F")
                .build();

        List<Tuple2<Object,Tuple2<Integer,List<Long>>>> vertices = Lists.newArrayList(
                new Tuple2<Object,Tuple2<Integer,List<Long>>>(1l, new Tuple2(0,Lists.newArrayList(Arrays.asList(1l)))),
                new Tuple2<Object,Tuple2<Integer,List<Long>>>(2l, new Tuple2(Integer.MAX_VALUE, Lists.newArrayList())),
                new Tuple2<Object,Tuple2<Integer,List<Long>>>(3l, new Tuple2(Integer.MAX_VALUE, Lists.newArrayList())),
                new Tuple2<Object,Tuple2<Integer,List<Long>>>(4l, new Tuple2(Integer.MAX_VALUE, Lists.newArrayList())),
                new Tuple2<Object,Tuple2<Integer,List<Long>>>(5l, new Tuple2(Integer.MAX_VALUE, Lists.newArrayList())),
                new Tuple2<Object,Tuple2<Integer,List<Long>>>(6l, new Tuple2(Integer.MAX_VALUE, Lists.newArrayList()))
        );

        List<Edge<Integer>> edges = Lists.newArrayList(
                new Edge<Integer>(1l,2l, 4), // A --> B (4)
                new Edge<Integer>(1l,3l, 2), // A --> C (2)
                new Edge<Integer>(2l,3l, 5), // B --> C (5)
                new Edge<Integer>(2l,4l, 10), // B --> D (10)
                new Edge<Integer>(3l,5l, 3), // C --> E (3)
                new Edge<Integer>(5l, 4l, 4), // E --> D (4)
                new Edge<Integer>(4l, 6l, 11) // D --> F (11)
        );

        JavaRDD<Tuple2<Object,Tuple2<Integer,List<Long>>>> verticesRDD = ctx.parallelize(vertices);
        JavaRDD<Edge<Integer>> edgesRDD = ctx.parallelize(edges);

        Graph<Tuple2<Integer, List<Long>>, Integer> G = Graph.apply(verticesRDD.rdd(), edgesRDD.rdd(),
                new Tuple2<Integer,List<Long>>(Integer.MAX_VALUE, Lists.newArrayList()),
                StorageLevel.MEMORY_ONLY(),
                StorageLevel.MEMORY_ONLY(),
                scala.reflect.ClassTag$.MODULE$.apply(Tuple2.class),
                scala.reflect.ClassTag$.MODULE$.apply(Integer.class));

        GraphOps ops = new GraphOps(G, scala.reflect.ClassTag$.MODULE$.apply(Tuple2.class),scala.reflect.ClassTag$.MODULE$.apply(Integer.class));

        ops.pregel(new Tuple2<Integer,List<Long>>(Integer.MAX_VALUE, Lists.newArrayList()),
                        Integer.MAX_VALUE,
                        EdgeDirection.Out(),
                        new VProg(),
                        new sendMsg(),
                        new merge(),
                        ClassTag$.MODULE$.apply(Tuple2.class))
                .vertices()
                .toJavaRDD().sortBy(f -> ((Tuple2<Object, Tuple2<Integer,List<Long>>>) f)._1, true, 0)
                .foreach(v -> {
                    Tuple2<Object,Tuple2<Integer,List<Long>>> vertex = (Tuple2<Object,Tuple2<Integer,List<Long>>>)v;
                    System.out.println(
                            "Minimum cost to get from "+labels.get(1l)
                                    +" to "+labels.get(vertex._1)
                                    +" is "+ vertex._2._2.stream().map(labels::get).collect(Collectors.toList())
                                    + " with cost "+vertex._2._1);
                });
    }
}
