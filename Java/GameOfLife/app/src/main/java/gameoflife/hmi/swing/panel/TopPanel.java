package gameoflife.hmi.swing.panel;

import java.awt.Dimension;
import java.awt.Font;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JSlider;
import javax.swing.SwingConstants;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import common.hmi.utils.HMIUtils;
import gameoflife.constants.HMIConstants;
import gameoflife.game.Game;
import gameoflife.game.GameStatusListener;
import gameoflife.hmi.swing.GameOfLifeMainViewFrame;
import gameoflife.hmi.swing.dialogs.DrawActionPickerPopup;

public class TopPanel extends BasePanel implements GameStatusListener {

	private static final Logger LOGGER = LogManager.getLogger(TopPanel.class);

	private static final long serialVersionUID = -4722225029326344692L;

	private JButton panButton;

	private JButton drawButton;

	private JSlider zoomLevelSlider;

	private JButton showGridButton;
	private JButton hideGridButton;

	@SuppressWarnings("unused")
	private GameOfLifeMainViewFrame gameOfLifeMainViewFrame;

	public TopPanel(GameOfLifeMainViewFrame gameOfLifeMainViewFrame, Game game) {
		this.gameOfLifeMainViewFrame = gameOfLifeMainViewFrame;

		setLayout(null);
		setBackground(HMIConstants.TOP_PANEL_BACKGROUND_COLOR);

		setPreferredSize(new Dimension(gameOfLifeMainViewFrame.getWidth(), HMIConstants.TOP_PANEL_HEIGHT));

		panButton = HMIUtils.createJButtonFromImagePathAndClass("PanButtonIcon.png", getClass());
		panButton.setLocation((int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getWidth(),
				(int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getHeight());
		panButton.addActionListener(e -> {
			LOGGER.info(() -> "Pan button actionned");
			hmiPresenter.togglePanInProgress();
		});
		add(panButton);

		drawButton = HMIUtils.createJButtonFromImagePathAndClass("DrawButtonIcon.png", getClass());
		drawButton.setLocation(
				(int) panButton.getBounds().getMaxX() + (int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getWidth(),
				(int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getHeight());
		drawButton.addActionListener(e -> {
			LOGGER.info(() -> "Draw button actionned");
			hmiPresenter.setDrawActionInProgress(null);
			new DrawActionPickerPopup(gameOfLifeMainViewFrame);
		});
		add(drawButton);

		zoomLevelSlider = new JSlider(SwingConstants.HORIZONTAL, HMIConstants.MINIMUM_CELL_SIZE_IN_PIXELS,
				HMIConstants.MAXIMUM_CELL_SIZE_IN_PIXELS, HMIConstants.MAXIMUM_CELL_SIZE_IN_PIXELS);
		zoomLevelSlider.setLocation(
				(int) drawButton.getBounds().getMaxX() + (int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getWidth(),
				(int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getHeight());
		zoomLevelSlider.setMajorTickSpacing(10);
		zoomLevelSlider.setMinorTickSpacing(1);
		zoomLevelSlider.setPaintTicks(false);
		zoomLevelSlider.setPaintLabels(false);
		zoomLevelSlider.setBorder(BorderFactory.createEmptyBorder(0, 0, 10, 0));
		Font font = new Font("Serif", Font.ITALIC, 15);
		zoomLevelSlider.setFont(font);
		zoomLevelSlider.setSize(new Dimension(100, drawButton.getHeight()));
		add(zoomLevelSlider);
		zoomLevelSlider.addChangeListener(e -> {
			hmiPresenter.setCellSizeInPixel(zoomLevelSlider.getValue());
		});

		JLabel zoomLevelStaticLabel = new JLabel("Zoom level");
		add(zoomLevelStaticLabel);
		zoomLevelStaticLabel.setLabelFor(zoomLevelSlider);

		showGridButton = HMIUtils.createJButtonFromImagePathAndClass("GridButtonIcon.png", getClass());
		showGridButton.setLocation(
				(int) zoomLevelSlider.getBounds().getMaxX()
						+ (int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getWidth(),
				(int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getHeight());
		showGridButton.setVisible(false);
		showGridButton.addActionListener(e -> {
			LOGGER.info(() -> "Show grid button actionned");
			hmiPresenter.displayGrid();

		});
		add(showGridButton);

		hideGridButton = HMIUtils.createJButtonFromImagePathAndClass("GridButtonIcon.png", getClass());
		hideGridButton.setLocation(
				(int) zoomLevelSlider.getBounds().getMaxX()
						+ (int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getWidth(),
				(int) HMIConstants.SPACE_BETWEEN_COMMANDS_DIMENSION.getHeight());
		hideGridButton.setVisible(false);
		hideGridButton.addActionListener(e -> {
			LOGGER.info(() -> "Show grid button actionned");
			hmiPresenter.hideGrid();

		});
		add(hideGridButton);

	}

	@Override
	public void onGameCancelled(Game game) {
		gameOfLifeMainViewFrame.removeTopPanel();
	}

	public void onGridHidden() {
		showGridButton.setVisible(true);
		hideGridButton.setVisible(false);
	}

	public void onGridDisplayed() {
		showGridButton.setVisible(false);
		hideGridButton.setVisible(true);
	}

	public void setCellSizeInPixel(int cellSizeInPixels) {
		zoomLevelSlider.setValue(cellSizeInPixels);
	}
}
