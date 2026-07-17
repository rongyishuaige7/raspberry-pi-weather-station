using System;
using System.Globalization;
using System.Linq;
using Avalonia.Controls;
using Avalonia.Threading;
using ScottPlot;
using WeatherStation.ViewModels;

namespace WeatherStation.Views;

public partial class HistoryView : UserControl
{
    private HistoryViewModel? _vm;

    public HistoryView()
    {
        InitializeComponent();
        DataContextChanged += OnDataContextChanged;
        // 如果 DataContext 在 InitializeComponent 之前已经设置，需在此补充订阅
        TrySubscribe(DataContext);
    }

    private void OnDataContextChanged(object? sender, EventArgs e)
    {
        if (_vm != null)
            _vm.QueryCompleted -= OnQueryCompleted;

        TrySubscribe(DataContext);
    }

    private void TrySubscribe(object? context)
    {
        _vm = context as HistoryViewModel;
        if (_vm != null)
            _vm.QueryCompleted += OnQueryCompleted;
    }

    private void OnQueryCompleted(object? sender, EventArgs e)
    {
        Dispatcher.UIThread.Post(RefreshPlot, DispatcherPriority.Background);
    }

    private void RefreshPlot()
    {
        if (_vm == null) return;

        var plt = Plot.Plot;
        plt.Clear();

        var n = _vm.Rows.Count;
        if (n == 0)
        {
            Plot.Refresh();
            return;
        }

        var xs = _vm.Rows
            .Select(r =>
            {
                if (DateTime.TryParse(r.RecordedAt, CultureInfo.InvariantCulture,
                        DateTimeStyles.None, out var dt))
                    return dt.ToOADate();
                return double.NaN;
            })
            .ToArray();

        var temps = _vm.Rows.Select(r => r.Temperature    ?? double.NaN).ToArray();
        var hums  = _vm.Rows.Select(r => r.Humidity       ?? double.NaN).ToArray();
        var lux   = _vm.Rows.Select(r => r.LightIntensity ?? double.NaN).ToArray();

        var s1 = plt.Add.Scatter(xs, temps);
        s1.LegendText = "温度(℃)";
        s1.Color      = new ScottPlot.Color(220, 60, 60);
        s1.LineWidth  = 2;
        s1.MarkerSize = 4;

        var s2 = plt.Add.Scatter(xs, hums);
        s2.LegendText = "湿度(%)";
        s2.Color      = new ScottPlot.Color(30, 130, 210);
        s2.LineWidth  = 2;
        s2.MarkerSize = 4;

        double luxMax = lux.Where(v => !double.IsNaN(v)).DefaultIfEmpty(1).Max();
        if (luxMax < 1) luxMax = 1;
        var luxNorm = lux.Select(v => double.IsNaN(v) ? v : v / luxMax * 100).ToArray();

        var s3 = plt.Add.Scatter(xs, luxNorm);
        s3.LegendText = string.Format("光照(%,max={0:F0}lux)", luxMax);
        s3.Color      = new ScottPlot.Color(200, 140, 0);
        s3.LineWidth  = 2;
        s3.MarkerSize = 4;

        plt.Axes.DateTimeTicksBottom();
        plt.Axes.Bottom.Label.Text = "时间";
        plt.Axes.Left.Label.Text   = "温度(℃) / 湿度(%) / 光照(归一化%)";

        plt.Legend.IsVisible  = true;
        plt.Legend.Alignment  = Alignment.UpperLeft;

        plt.Axes.AutoScale();
        Plot.Refresh();
    }
}
