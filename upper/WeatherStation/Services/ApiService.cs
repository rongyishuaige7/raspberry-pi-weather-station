using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using WeatherStation.Models;

namespace WeatherStation.Services;

public sealed class ApiService
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    };

    private readonly HttpClient _http = new();

    public string BaseUrl { get; set; } = "http://127.0.0.1:5000";

    public string? Token { get; set; }

    private HttpRequestMessage Request(HttpMethod method, string relative, HttpContent? content = null)
    {
        var uri = new Uri(new Uri(BaseUrl.TrimEnd('/') + "/"), relative.TrimStart('/'));
        var req = new HttpRequestMessage(method, uri);
        if (!string.IsNullOrEmpty(Token))
            req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", Token);
        if (content != null)
            req.Content = content;
        return req;
    }

    private static string NetworkErrorMessage(Exception ex)
    {
        if (ex is HttpRequestException { InnerException: System.Net.Sockets.SocketException se })
            return $"无法连接到服务器，请检查 IP 和端口是否正确（{se.Message}）";
        if (ex is HttpRequestException hre)
            return $"网络请求失败: {hre.Message}";
        if (ex is TaskCanceledException)
            return "请求超时，服务器无响应";
        return $"未知错误: {ex.Message}";
    }

    public async Task<ApiEnvelope<T?>> GetAsync<T>(string path)
    {
        try
        {
            using var resp = await _http.SendAsync(Request(HttpMethod.Get, path));
            var json = await resp.Content.ReadAsStringAsync();
            var env = JsonSerializer.Deserialize<ApiEnvelope<T?>>(json, JsonOptions);
            return env ?? new ApiEnvelope<T?> { Code = -1, Message = "空响应" };
        }
        catch (Exception ex)
        {
            return new ApiEnvelope<T?> { Code = -1, Message = NetworkErrorMessage(ex) };
        }
    }

    public async Task<ApiEnvelope<T?>> PostJsonAsync<T>(string path, object body)
    {
        try
        {
            var json = JsonSerializer.Serialize(body, JsonOptions);
            using var content = new StringContent(json, Encoding.UTF8, "application/json");
            using var resp = await _http.SendAsync(Request(HttpMethod.Post, path, content));
            var text = await resp.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<ApiEnvelope<T?>>(text, JsonOptions)
                   ?? new ApiEnvelope<T?> { Code = -1, Message = text };
        }
        catch (Exception ex)
        {
            return new ApiEnvelope<T?> { Code = -1, Message = NetworkErrorMessage(ex) };
        }
    }

    public async Task<ApiEnvelope<T?>> PutJsonAsync<T>(string path, object body)
    {
        try
        {
            var json = JsonSerializer.Serialize(body, JsonOptions);
            using var content = new StringContent(json, Encoding.UTF8, "application/json");
            using var resp = await _http.SendAsync(Request(HttpMethod.Put, path, content));
            var text = await resp.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<ApiEnvelope<T?>>(text, JsonOptions)
                   ?? new ApiEnvelope<T?> { Code = -1, Message = text };
        }
        catch (Exception ex)
        {
            return new ApiEnvelope<T?> { Code = -1, Message = NetworkErrorMessage(ex) };
        }
    }

    public async Task<ApiEnvelope<object?>> DeleteAsync(string path)
    {
        try
        {
            using var resp = await _http.SendAsync(Request(HttpMethod.Delete, path));
            var text = await resp.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<ApiEnvelope<object?>>(text, JsonOptions)
                   ?? new ApiEnvelope<object?> { Code = -1, Message = text };
        }
        catch (Exception ex)
        {
            return new ApiEnvelope<object?> { Code = -1, Message = NetworkErrorMessage(ex) };
        }
    }
}
