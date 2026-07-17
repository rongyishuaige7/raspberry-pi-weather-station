using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using WeatherStation.Models;
using WeatherStation.Services;

namespace WeatherStation.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    private readonly ApiService _api = new();

    [ObservableProperty] private string _apiBaseUrl = AppSettings.ApiBaseUrl;

    [ObservableProperty] private bool _isAuthenticated;

    [ObservableProperty] private string _loginUsername = "";

    [ObservableProperty] private string _loginPassword = "";

    [ObservableProperty] private string _registerUsername = "";

    [ObservableProperty] private string _registerPassword = "";

    [ObservableProperty] private string _oldPassword = "";

    [ObservableProperty] private string _newPassword = "";

    [ObservableProperty] private string _authStatus = "";

    [ObservableProperty] private string _currentUser = "";

    public DashboardViewModel Dashboard { get; }

    public HistoryViewModel History { get; }

    public AlarmViewModel Alarms { get; }

    public SettingsViewModel Settings { get; }

    public DeviceViewModel Devices { get; }

    public MainWindowViewModel()
    {
        _api.BaseUrl = ApiBaseUrl;
        Settings = new SettingsViewModel(_api);
        Dashboard = new DashboardViewModel(_api, Settings);
        History = new HistoryViewModel(_api);
        Alarms = new AlarmViewModel(_api);
        Devices = new DeviceViewModel(_api);
    }

    partial void OnApiBaseUrlChanged(string value)
    {
        var url = value.Trim();
        _api.BaseUrl = url;
        AppSettings.ApiBaseUrl = url;   // 自动持久化到本地文件
    }

    [RelayCommand]
    private async Task ApplyBaseUrlAsync()
    {
        _api.BaseUrl = ApiBaseUrl.Trim();
        AuthStatus = $"已设置服务地址: {_api.BaseUrl}";
        await Task.CompletedTask;
    }

    [RelayCommand]
    private async Task LoginAsync()
    {
        AuthStatus = "登录中…";
        var env = await _api.PostJsonAsync<LoginData>(
            "/api/auth/login",
            new { username = LoginUsername, password = LoginPassword });
        if (env.Code != 200 || env.Data?.Token == null)
        {
            AuthStatus = env.Message ?? "登录失败";
            IsAuthenticated = false;
            return;
        }

        _api.Token = env.Data.Token;
        IsAuthenticated = true;
        CurrentUser = env.Data.Username ?? LoginUsername;
        AuthStatus = "登录成功";
        // 先加载最新阈值，Dashboard 轮询时即可使用正确的告警阈值
        await Settings.LoadCommand.ExecuteAsync(null);
        Dashboard.StartPolling();
    }

    [RelayCommand]
    private async Task RegisterAsync()
    {
        AuthStatus = "注册中…";
        var env = await _api.PostJsonAsync<object>(
            "/api/auth/register",
            new { username = RegisterUsername, password = RegisterPassword });
        AuthStatus = env.Code == 200 ? "注册成功，请登录" : env.Message ?? "注册失败";
        await Task.CompletedTask;
    }

    [RelayCommand]
    private void Logout()
    {
        Dashboard.StopPolling();
        _api.Token = null;
        IsAuthenticated = false;
        CurrentUser = "";
        AuthStatus = "已注销";
    }

    [RelayCommand]
    private async Task ChangePasswordAsync()
    {
        var env = await _api.PostJsonAsync<object>(
            "/api/auth/password",
            new { old_password = OldPassword, new_password = NewPassword });
        AuthStatus = env.Code == 200 ? "密码已修改" : env.Message ?? "修改失败";
        await Task.CompletedTask;
    }
}
