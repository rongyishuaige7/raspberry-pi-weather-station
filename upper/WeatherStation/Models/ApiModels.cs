using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace WeatherStation.Models;

public class ApiEnvelope<T>
{
    [JsonPropertyName("code")]
    public int Code { get; set; }

    [JsonPropertyName("message")]
    public string? Message { get; set; }

    [JsonPropertyName("data")]
    public T? Data { get; set; }
}

public class LoginData
{
    [JsonPropertyName("token")]
    public string? Token { get; set; }

    [JsonPropertyName("username")]
    public string? Username { get; set; }

    [JsonPropertyName("role")]
    public string? Role { get; set; }
}

public class SensorDataRow
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("temperature")]
    public double? Temperature { get; set; }

    [JsonPropertyName("humidity")]
    public double? Humidity { get; set; }

    [JsonPropertyName("light_intensity")]
    public double? LightIntensity { get; set; }

    [JsonPropertyName("recorded_at")]
    public string? RecordedAt { get; set; }
}

public class AlarmRow
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("param_name")]
    public string? ParamName { get; set; }

    [JsonPropertyName("param_value")]
    public double ParamValue { get; set; }

    [JsonPropertyName("threshold_value")]
    public double ThresholdValue { get; set; }

    [JsonPropertyName("alarm_type")]
    public string? AlarmType { get; set; }

    [JsonPropertyName("triggered_at")]
    public string? TriggeredAt { get; set; }

    [JsonPropertyName("acknowledged")]
    public int Acknowledged { get; set; }
}

public class DeviceRow
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("device_name")]
    public string? DeviceName { get; set; }

    [JsonPropertyName("device_no")]
    public string? DeviceNo { get; set; }

    [JsonPropertyName("location")]
    public string? Location { get; set; }

    [JsonPropertyName("status")]
    public string? Status { get; set; }

    [JsonPropertyName("created_at")]
    public string? CreatedAt { get; set; }
}
