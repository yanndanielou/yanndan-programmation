package hmi;

import java.util.HashMap;

import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.JLayeredPane;

import belligerents.Attacker;
import belligerents.Tower;
import belligerents.listeners.AttackerListener;
import belligerents.listeners.TowerListener;
import game.Game;
import game.GameBoardPointListener;
import game.GameStatusListener;
import game_board.GameBoard;

public class GameFieldPanel extends JLayeredPane
		implements GameStatusListener, GameBoardPointListener, TowerListener, AttackerListener {

	private static final long serialVersionUID = -1541008040602802454L;

	private ImageIcon empty_game_board_full_as_icon = new ImageIcon("Images/Empty_game_board_full.png");
	private JLabel empty_game_board_full_as_label;

	private HashMap<Tower, JLabel> tower_to_label_map = new HashMap<>();

	private enum LAYERS_ORDERED_FROM_TOP_TO_BACK {
		BELLIGERENTS, BACKGROUND_IMAGE, UNVISIBLE;
	}

	private DesktopTowerDefenseMainViewFrame DesktopTowerDefenseMainViewFrame;;

	public GameFieldPanel(DesktopTowerDefenseMainViewFrame DesktopTowerDefenseMainViewFrame) {
		this.DesktopTowerDefenseMainViewFrame = DesktopTowerDefenseMainViewFrame;
	}

	public void initialize_gamefield(GameBoard gameField) {
		setLayout(null);
		setSize(gameField.getTotalWidth(), gameField.getTotalHeight());

		empty_game_board_full_as_label = new JLabel(empty_game_board_full_as_icon);

		empty_game_board_full_as_label.setSize(gameField.getTotalWidth(), gameField.getTotalHeight());
		empty_game_board_full_as_label.setLocation(0, 0);

		add(empty_game_board_full_as_label, LAYERS_ORDERED_FROM_TOP_TO_BACK.BACKGROUND_IMAGE.ordinal());

	}

	@Override
	public void on_listen_to_game_status(Game game) {
		// TODO Auto-generated method stub

	}

	@Override
	public void on_game_cancelled(Game game) {
		removeAll();
		DesktopTowerDefenseMainViewFrame.removeGameFieldPanel();
	}

	@Override
	public void on_game_lost(Game game) {
	}

	@Override
	public void on_game_won(Game game) {
		// TODO Auto-generated method stub
	}

	@Override
	public void on_listen_to_tower(Tower tower) {
		ImageIcon get_graphical_representation_as_icon = tower.get_graphical_representation_as_icon();
		JLabel tower_as_label = new JLabel(get_graphical_representation_as_icon);
		tower_as_label.setLocation((int) tower.getSurrounding_rectangle_absolute_on_complete_board().getX(),
				(int) tower.getSurrounding_rectangle_absolute_on_complete_board().getY());
		tower_as_label.setSize((int) tower.getSurrounding_rectangle_absolute_on_complete_board().getWidth(),
				(int) tower.getSurrounding_rectangle_absolute_on_complete_board().getHeight());
		tower_to_label_map.put(tower, tower_as_label);
		add(tower_as_label, LAYERS_ORDERED_FROM_TOP_TO_BACK.BELLIGERENTS.ordinal());
		// repaint();
	}

	@Override
	public void on_attacker_end_of_destruction_and_clean(Attacker attacker) {
		// TODO Auto-generated method stub

	}

	@Override
	public void on_listen_to_attacker(Attacker attacker) {
		// TODO Auto-generated method stub

	}

	@Override
	public void on_attacker_moved(Attacker attacker) {
		// TODO Auto-generated method stub

	}

	@Override
	public void on_attacker_beginning_of_destruction(Attacker attacker) {
		// TODO Auto-generated method stub

	}

}