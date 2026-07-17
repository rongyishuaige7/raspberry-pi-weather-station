using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using WeatherStation.Models;
using WeatherStation.Services;

namespace WeatherStation.ViewModels;

public partial class HistoryViewModel : ViewModelBase
{
    private readonly ApiService _api;

    /// <summary>查询完成后触发，供视图刷新曲线。</summary>
    public event EventHandler? QueryCompleted;

    // Avalonia DatePicker.SelectedDate 是 DateTimeOffset?，必须用 nullable 类型才能双向绑定
    private DateTimeOffset? _start = DateTimeOffset.Now.Date;
    private DateTimeOffset? _end   = DateTimeOffset.Now.Date;

    public DateTimeOffset? Start
    {
        get => _start;
        set => SetProperty(ref _start, value);
    }

    public DateTimeOffset? End
    {
        get => _end;
        set => SetProperty(ref _end, value);
    }

    [ObservableProperty] private string _status = "";
    [ObservableProperty] private SensorDataRow? _selectedRow;

    public ObservableCollection<SensorDataRow> Rows { get; } = new();

    public HistoryViewModel(ApiService api)
    {
        _api = api;
    }

    [RelayCommand]
    private async Task LoadAsync()
    {
        Status = "加载中…";
        Rows.Clear();

        // 用所选日期的 00:00:00 ~ 23:59:59 作为查询范围
        var startDt = (Start ?? DateTimeOffset.Now).Date;
        var endDt   = (End   ?? DateTimeOffset.Now).Date.AddDays(1).AddSeconds(-1);
        var start = startDt.ToString("yyyy-MM-dd HH:mm:ss");
        var end   = endDt.ToString("yyyy-MM-dd HH:mm:ss");
        var path = $"/api/history?start={Uri.EscapeDataString(start)}&end={Uri.EscapeDataString(end)}";
        var env = await _api.GetAsync<SensorDataRow[]>(path);
        if (env.Code != 200)
        {
            Status = env.Message ?? $"错误 {env.Code}";
            return;
        }

        var data = env.Data;
        if (data == null)
        {
            Status = "无数据";
            return;
        }

        foreach (var r in data)
            Rows.Add(r);
        Status = $"共 {Rows.Count} 条";
        QueryCompleted?.Invoke(this, EventArgs.Empty);
    }

    [RelayCommand]
    private async Task DeleteSelectedAsync()
    {
        if (SelectedRow == null)
        {
            Status = "请先在表格中选中一行";
            return;
        }

        var row = SelectedRow;
        var env = await _api.DeleteAsync($"/api/history/{row.Id}");
        if (env.Code == 200)
        {
            Rows.Remove(row);
            SelectedRow = null;
            Status = $"已删除 ID={row.Id}，剩余 {Rows.Count} 条";
        }
        else
        {
            Status = $"删除失败: {env.Message}";
        }
    }

    [RelayCommand]
    private async Task DeleteRangeAsync()
    {
        var startDt = (Start ?? DateTimeOffset.Now).Date;
        var endDt   = (End   ?? DateTimeOffset.Now).Date.AddDays(1).AddSeconds(-1);
        var start = startDt.ToString("yyyy-MM-dd HH:mm:ss");
        var end   = endDt.ToString("yyyy-MM-dd HH:mm:ss");
        var path = $"/api/history?start={Uri.EscapeDataString(start)}&end={Uri.EscapeDataString(end)}";
        Status = "删除中…";
        var env = await _api.DeleteAsync(path);
        if (env.Code == 200)
        {
            Rows.Clear();
            SelectedRow = null;
            Status = env.Message ?? "已删除当前日期范围内的数据";
        }
        else
        {
            Status = $"删除失败: {env.Message}";
        }
    }

    [RelayCommand]
    private async Task DeleteAllAsync()
    {
        Status = "删除所有数据中…";
        var env = await _api.DeleteAsync("/api/history");
        if (env.Code == 200)
        {
            Rows.Clear();
            SelectedRow = null;
            Status = env.Message ?? "已清空所有历史数据";
        }
        else
        {
            Status = $"删除失败: {env.Message}";
        }
    }
}
