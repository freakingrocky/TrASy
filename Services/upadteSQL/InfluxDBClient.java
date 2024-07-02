public class InfluxDBClient {
    static {
        System.loadLibrary("InfluxDBClient"); // Load the DLL/SO library
    }

    // Declare the native method
    public native void performFluxQuery(String fluxQuery);

    public static void main(String[] args) {
        InfluxDBClient client = new InfluxDBClient();
        client.performFluxQuery("from(bucket: \"your-bucket\") |> range(start: -1h)");
    }
}
