using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net.Sockets;
using UnityEngine;

[System.Serializable]
public struct sensor
{
    public Vector3 relativePos;
    public float angle;
}

public class droneConfig : MonoBehaviour {

    public GameObject droneBody;
    public List<sensor> sensors;

    private TcpClient client;
    private Stream s;
    private StreamReader sr;

	private Vector3 position = new Vector3(0,0,0);
	private float angle = 0;
	private List<float> sensorMeasurements = new List<float>();

    private List<LineRenderer> lines = new List<LineRenderer>();
    public string received;
    // Use this for initialization
    void Start () {

        // add line renders to each sensro and add them to a list for easy access
        foreach (sensor go in sensors)
        {
            GameObject gameObj = Instantiate(new GameObject(), gameObject.transform);
            LineRenderer lr = gameObj.AddComponent<LineRenderer>();
            lr.SetPosition(0, gameObject.transform.position + go.relativePos);
            lr.startWidth = (float)0.01;
            lr.endWidth = (float)0.01;
            lr.startColor = Color.red;
            lr.endColor = Color.red;
            lr.useWorldSpace = true;
            lines.Add(lr);
        }

        //init socket:
        client = new TcpClient("127.0.0.1", 12340);

		
        s = client.GetStream();
        sr = new StreamReader(s);
    }
	
	// Update is called once per frame
	void Update () {
		
		string line = sr.ReadLine();
		

		if (!string.IsNullOrEmpty(line))
		{
			string[] elements = line.Split(',', ' ');
			if (elements[0].Equals("p"))
			{
				// position data
				position = new Vector3(float.Parse(elements[1]), float.Parse(elements[2]), float.Parse(elements[3]));
				angle = float.Parse(elements[4]);
				
			}else if (elements[0].Equals("m"))
			{
				sensorMeasurements.Clear();
				for(int i = 1; i < elements.Length; i++)
				{
					sensorMeasurements.Add(float.Parse(elements[i]));
				}
				
			}
			received = line;
			updateDronePosition(position, angle);
			drawSensorData(sensorMeasurements);
			//s.Close();
			//client.Close();
		}
		
        //drawSensorData(mes);
        //updateDronePosition(transform.position.x + (float)0.001, transform.position.y, transform.position.z, a);
    }

    private void updateDronePosition(Vector3 pos, float angle)
    {
        transform.SetPositionAndRotation(pos, Quaternion.AngleAxis(angle, Vector3.up));
    }

    private void drawSensorData(List<float> measurments)
    {
        if(measurments.Count != sensors.Count)
        {
            throw new System.Exception("number of received sensor measurments did not match the number of sensors configured in viz tool.");
        }
        for(int i = 0; i < sensors.Count; i++)
        {
            Vector3 startPoint = gameObject.transform.position + transform.rotation * sensors[i].relativePos;
            Vector3 endPoint = startPoint;
            Quaternion rot = transform.rotation;
            Vector3 rotEuler = rot.eulerAngles;
            rotEuler.y += sensors[i].angle;
            rot.eulerAngles = rotEuler;
            endPoint = endPoint + rot * (Vector3.forward * measurments[i]);
            lines[i].SetPosition(0, startPoint);
            lines[i].SetPosition(1, endPoint);
        }
    }

    private void OnApplicationQuit()
    {
        s.Close();
        client.Close();
    }
}
